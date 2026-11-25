# M61 capture audit (2026-11-18): the records each M61 page now captures,
# exercised as freshly created NON-ADMIN users through the real actions (the
# superuser is trusted by the field guard and would hide a gap). The
# odoo_env fixture rolls everything back.
import contextlib
import itertools

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

PUBLISHER = "cd_knowledge.group_knowledge_publisher"
QM = "cd_qms_process.group_qms_quality_manager"
GUARD = "changes only through its workflow"
_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M61 %s %d" % (login, n),
                "login": "m61cap.%s.%d@m61.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


@contextlib.contextmanager
def refused(env, exc, match):
    """A constraint refuses after the row exists: roll it back with the
    refusal, as a request would (pytest.raises outside the savepoint)."""
    with pytest.raises(exc, match=match), env.cr.savepoint():
        yield


def _branch(env):
    branch = env["fix.branch"].search([], limit=1)
    if branch:
        return branch
    unit = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "M61 Unit", "code": "M61U", "company_id": env.company.id}
    )
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "M61 Group Ltd",
            "code": "M61G",
            "company_id": env.company.id,
            "operating_unit_id": unit.id,
        }
    )
    return env["fix.branch"].create(
        {"name": "M61 Hub", "code": "M61-HUB", "entity_id": entity.id, "operating_unit_id": unit.id}
    )


class W:
    pass


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    if not env.ref(QM, raise_if_not_found=False):
        pytest.skip("the safety sign-off needs the Quality Manager group (cd_qms_process)")
    x = W()
    x.env = env
    x.tech = _user(env, "tech")
    x.tech2 = _user(env, "tech2")
    x.author = _user(env, "author", [PUBLISHER])
    x.publisher = _user(env, "publisher", [PUBLISHER])
    x.publisher2 = _user(env, "publisher2", [PUBLISHER])
    x.qm = _user(env, "qm", [QM])
    n = next(_SEQ)
    x.brand = env["fix.brand"].create({"name": "Zeltrix%d" % n, "code": "ZX%d" % n})
    x.model = env["fix.device.model"].create({"name": "Z14-%d" % n, "brand_id": x.brand.id})
    x.model2 = env["fix.device.model"].create({"name": "Z15-%d" % n, "brand_id": x.brand.id})
    x.fault = env["fix.fault.code"].create(
        {"code": "M61-%d" % n, "name": "No power M61 %d" % n, "category": "power"}
    )
    return x


def _article(x, user=None, **vals):
    base = {
        "name": "Z14 no-power fix %d" % next(_SEQ),
        "category": "repair_procedure",
        "content": "<p>Check the PMIC rail.</p>",
        "device_brand": x.brand.name,
        "device_model": x.model.name,
    }
    base.update(vals)
    return x.env["fix.knowledge.article"].with_user(user or x.author).create(base)


def _publish(x, art, by=None):
    art.with_user(by or x.publisher).action_publish()
    assert art.state == "published"
    return art


# ================================================================ page 1: field capture
def test_a_technician_captures_in_their_own_words_and_cannot_forge_who(w):
    Capture = w.env["fix.knowledge.capture"].with_user(w.tech)
    cap = Capture.create(
        {"raw_text": "PMIC গরম হচ্ছিল, রিফ্লো করে ঠিক হয়েছে", "device_brand": w.brand.name}
    )
    assert cap.state == "queued" and cap.captured_by_id == w.tech
    assert cap.name.startswith("KCAP/")
    with pytest.raises(UserError, match=GUARD):
        Capture.create({"raw_text": "x", "captured_by_id": w.tech2.id})
    # the contributor corrects it while it waits; nobody else does
    cap.write({"raw_text": "PMIC overheated; reflowed it"})
    with pytest.raises(UserError, match="BRU-KMS-09"):
        cap.with_user(w.tech2).write({"raw_text": "rewritten by someone else"})


def test_a_capture_is_structured_by_another_publisher_keeping_the_words(w):
    cap = (
        w.env["fix.knowledge.capture"]
        .with_user(w.author)
        .create(
            {
                "raw_text": "Line one title\nreflow the PMIC at 350C",
                "fault_code_id": w.fault.id,
                "device_brand": w.brand.name,
                "device_model": w.model.name,
                "rework_level": "L3",
            }
        )
    )
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        cap.with_user(w.tech).action_take()
    # the contributor does not structure their own capture
    with pytest.raises(UserError, match="your own capture"):
        cap.with_user(w.author).action_take()
    cap.with_user(w.publisher).action_take()
    assert (cap.state, cap.reviewer_id) == ("taken", w.publisher)
    # its words are frozen once taken, even for the contributor
    with pytest.raises(UserError, match="BRU-KMS-09"):
        cap.with_user(w.author).write({"raw_text": "changed later"})
    with pytest.raises(UserError, match="being structured by"):
        cap.with_user(w.publisher2).action_draft_article()
    cap.with_user(w.publisher).action_draft_article()
    art = cap.article_id
    assert cap.state == "drafted" and art.state == "draft"
    assert art.original_capture_text == cap.raw_text
    assert (art.contributor_id, art.capture_id, art.name) == (w.author, cap, "Line one title")
    assert art.rework_level == "L3" and art.device_model == w.model.name
    assert art.link_ids.fault_code_id == w.fault
    # neither the structurer nor the contributor publishes it unreviewed
    with pytest.raises(UserError, match="You wrote"):
        art.with_user(w.publisher).action_publish()
    with pytest.raises(UserError, match="You wrote"):
        art.with_user(w.author).action_publish()
    _publish(w, art, by=w.publisher2)
    with pytest.raises(UserError, match=GUARD):
        art.with_user(w.publisher2).write({"original_capture_text": "edited"})


def test_a_capture_merges_into_the_article_that_covers_it(w):
    existing = _article(w, article_code="KB-M61-MERGE")
    cap = w.env["fix.knowledge.capture"].with_user(w.tech).create({"raw_text": "same as KB"})
    cap.with_user(w.publisher).action_take()
    with pytest.raises(UserError, match="Name the article"):
        cap.with_user(w.publisher).action_merge("")
    cap.with_user(w.publisher).action_merge("kb-m61-merge")
    assert (cap.state, cap.article_id) == ("merged", existing)
    assert any("same as KB" in (m.body or "") for m in existing.message_ids)
    with pytest.raises(AccessError):
        cap.with_user(w.tech).unlink()


def test_a_capture_on_a_job_takes_the_jobs_device_and_fault(w):
    env = w.env
    branch = _branch(env)
    customer = env["res.partner"].create({"name": "M61 capture customer"})
    device = env["fix.device"].create(
        {
            "device_model_id": w.model.id,
            "owner_id": customer.id,
            "serial_number": "SN-M61-%d" % next(_SEQ),
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "No power",
        }
    )
    env["fix.service.order.fault"].create(
        {"order_id": order.id, "fault_code": w.fault.code, "description": "No power"}
    )
    cap = (
        env["fix.knowledge.capture"]
        .with_user(w.tech)
        .create({"raw_text": "fixed it", "service_order_id": order.id})
    )
    assert (cap.device_brand, cap.device_model, cap.fault_code_id) == (
        w.brand.name,
        w.model.name,
        w.fault,
    )


# ================================================================ page 1: review requests
def test_a_review_is_requested_from_a_qualified_non_author_on_draft_content(w):
    art = _article(w)
    Review = w.env["fix.knowledge.review"].with_user(w.author)
    with pytest.raises(UserError, match="must be a Knowledge Publisher"):
        Review.create({"article_id": art.id, "reviewer_id": w.tech.id})
    with pytest.raises(UserError, match="cannot be its author"):
        Review.create({"article_id": art.id, "reviewer_id": w.author.id})
    with refused(w.env, ValidationError, "one article or one tree"):
        Review.create({"reviewer_id": w.publisher.id})
    rev = Review.create({"article_id": art.id, "reviewer_id": w.publisher.id})
    assert rev.state == "requested" and rev.content_hash == art.content_hash
    assert rev.name.startswith("KREV/")
    with pytest.raises(UserError, match="already has an open review"):
        Review.create({"article_id": art.id, "reviewer_id": w.publisher2.id})
    # the request names its content and reviewer for good
    with pytest.raises(UserError, match="names its content and reviewer"):
        rev.write({"reviewer_id": w.publisher2.id})
    with pytest.raises(UserError, match=GUARD):
        rev.write({"state": "approved"})
    published = _publish(w, _article(w))
    with pytest.raises(UserError, match="a review is requested for draft content"):
        Review.create({"article_id": published.id, "reviewer_id": w.publisher2.id})


def test_only_the_reviewer_decides_and_a_return_says_why(w):
    art = _article(w)
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art.id, "reviewer_id": w.publisher.id})
    )
    with pytest.raises(UserError, match="Only .* reviews"):
        rev.with_user(w.publisher2).action_approve()
    with pytest.raises(UserError, match="Say what the author should change"):
        rev.with_user(w.publisher).action_return("  ")
    with pytest.raises(UserError, match="Only the reviewer"):
        rev.with_user(w.publisher2).action_return("not yours")
    rev.with_user(w.publisher).action_return("Add the torque values")
    assert (rev.state, rev.comments) == ("returned", "Add the torque values")
    # a new request after the author's edit
    art.with_user(w.author).write({"content": "<p>Check the PMIC rail; torque 0.2 Nm.</p>"})
    rev2 = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art.id, "reviewer_id": w.publisher.id})
    )
    rev2.with_user(w.publisher).action_approve("Good")
    assert rev2.state == "approved"
    # the approved review names the reviewer — even when the AUTHOR publishes
    art.with_user(w.author).action_publish()
    assert (art.state, art.reviewed_by_id) == ("published", w.publisher)


def test_an_edit_after_the_request_needs_a_new_review(w):
    art = _article(w, tags="battery")  # safety-critical
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art.id, "reviewer_id": w.publisher.id})
    )
    assert rev.safety_required
    art.with_user(w.author).write({"content": "<p>changed after the request</p>"})
    assert rev.content_changed
    with pytest.raises(UserError, match="has changed since"):
        rev.with_user(w.publisher).action_approve()


def test_safety_content_needs_the_quality_managers_sign_off(w):
    art = _article(w, tags="high voltage")
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art.id, "reviewer_id": w.publisher.id})
    )
    rev.with_user(w.publisher).action_approve()
    assert rev.state == "reviewed"
    with pytest.raises(UserError, match="only through an approved review"):
        art.with_user(w.publisher2).action_publish()
    with pytest.raises(UserError, match="Only the Quality Manager"):
        rev.with_user(w.publisher2).action_safety_approve()
    # a QM who reviewed it does not also sign it off
    w.publisher.write({"group_ids": [(4, w.env.ref(QM).id)]})
    with pytest.raises(UserError, match="neither wrote nor reviewed"):
        rev.with_user(w.publisher).action_safety_approve()
    rev.with_user(w.qm).action_safety_approve()
    assert (rev.state, rev.safety_approved_by_id) == ("approved", w.qm)
    art.with_user(w.publisher2).action_publish()
    assert art.reviewed_by_id == w.publisher
    # an approval covers the reviewed content only: a typed reviewer is refused
    art2 = _article(w)
    rev2 = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art2.id, "reviewer_id": w.publisher.id})
    )
    rev2.with_user(w.publisher).action_approve()
    with pytest.raises(UserError, match="publishing names that review"):
        art2.with_user(w.publisher2).action_publish(reviewer_id=w.publisher2.id)


def test_ordinary_content_takes_no_typed_reviewer(w):
    """BRU-KMS-02: a reviewer is named by an approved review, never typed at
    publication - the old K1 kwarg let a publisher name a colleague who had
    reviewed nothing."""
    art = _article(w)
    assert not art.safety_critical
    with pytest.raises(UserError, match="not typed at publication"):
        art.with_user(w.publisher).action_publish(reviewer_id=w.publisher2.id)
    assert art.state == "draft" and not art.reviewed_by_id


def test_a_review_is_cancelled_by_its_requester_or_a_publisher(w):
    art = _article(w)
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"article_id": art.id, "reviewer_id": w.publisher.id})
    )
    with pytest.raises(UserError, match="cancels it"):
        rev.with_user(w.tech).action_cancel()
    rev.with_user(w.author).action_cancel()
    assert rev.state == "cancelled"


# ================================================================ page 1: version history
def test_each_published_version_is_kept_and_never_typed(w):
    art = _article(w)
    _publish(w, art)
    art.with_user(w.author).write({"content": "<p>Revised: check the PMIC rail at 1.8V.</p>"})
    versions = art.version_ids.sorted("version")
    assert versions.mapped("version") == [2, 3]
    assert versions.mapped("change_note") == ["published", "revised"]
    assert "1.8V" in versions[-1].content and "1.8V" not in versions[0].content
    with pytest.raises((AccessError, UserError)):
        w.env["fix.knowledge.article.version"].with_user(w.publisher).create(
            {"article_id": art.id, "version": 9, "change_note": "published"}
        )
    with pytest.raises((AccessError, UserError)):
        versions[0].with_user(w.publisher).write({"content": "<p>rewritten history</p>"})


# ================================================================ page 2: tree steps
def test_tree_steps_change_only_while_draft_and_are_reviewed(w):
    tree = (
        w.env["fix.knowledge.tree"]
        .with_user(w.author)
        .create(
            {
                "name": "Z14 no power",
                "device_brand": w.brand.name,
                "node_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 10,
                            "node_type": "measurement",
                            "text": "PP_VDD_MAIN",
                            "expected": "3.8V",
                            "yes_next": "20",
                            "no_next": "Replace PMIC",
                        },
                    )
                ],
            }
        )
    )
    assert tree.node_count == 1
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"tree_id": tree.id, "reviewer_id": w.publisher.id})
    )
    tree.node_ids.with_user(w.author).write({"expected": "4.2V"})
    assert rev.content_changed  # the steps are part of what was reviewed
    rev.with_user(w.publisher).action_return("re-request")
    rev = (
        w.env["fix.knowledge.review"]
        .with_user(w.author)
        .create({"tree_id": tree.id, "reviewer_id": w.publisher.id})
    )
    rev.with_user(w.publisher).action_approve()
    tree.with_user(w.publisher2).action_publish()
    assert (tree.state, tree.reviewed_by_id) == ("published", w.publisher)
    with pytest.raises(UserError, match="only while the tree is a draft"):
        tree.node_ids.with_user(w.author).write({"expected": "5V"})
    with pytest.raises(UserError, match="only while the tree is a draft"):
        w.env["fix.knowledge.tree.node"].with_user(w.author).create(
            {"tree_id": tree.id, "text": "late step"}
        )
    with pytest.raises(UserError, match="only while the tree is a draft"):
        tree.node_ids.with_user(w.author).unlink()


# ================================================================ page 3: library entries
def test_a_library_entry_is_registered_with_its_file_models_and_terms(w):
    Library = w.env["fix.knowledge.library"]
    with pytest.raises(AccessError):
        Library.with_user(w.tech).create({"name": "Z14 service manual", "brand_id": w.brand.id})
    entry = Library.with_user(w.publisher).create(
        {"name": "Z14 service manual", "brand_id": w.brand.id, "entry_type": "service_manual"}
    )
    with pytest.raises(UserError, match="the file.*the models it covers.*licence"):
        entry.with_user(w.publisher).action_make_available()
    att = (
        w.env["ir.attachment"]
        .with_user(w.publisher)
        .create({"name": "z14.pdf", "datas": "JVBERi0xLjQK"})
    )
    entry.with_user(w.publisher).write(
        {
            "document_attachment_id": att.id,
            "device_model_ids": [(6, 0, [w.model.id])],
            "licence_terms": "Internal use; no redistribution to customers",
            "redistribution": "technicians",
        }
    )
    assert entry.offline_allowed
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        entry.with_user(w.tech).action_make_available()
    entry.with_user(w.publisher).action_make_available()
    assert (entry.state, entry.made_available_by_id) == ("available", w.publisher)
    with pytest.raises(UserError, match="are fixed"):
        entry.with_user(w.publisher).write({"redistribution": "internal_desk"})
    with pytest.raises(UserError, match="Say why"):
        entry.with_user(w.publisher).action_withdraw("")
    entry.with_user(w.publisher).action_withdraw("New edition received")
    assert entry.state == "withdrawn"
    with pytest.raises(UserError, match=GUARD):
        entry.with_user(w.publisher).write({"state": "available"})


# ================================================================ page 4: links + surfacing
def test_a_link_names_one_content_and_one_subject_and_drives_surfacing(w):
    Link = w.env["fix.knowledge.link"].with_user(w.tech)
    art = _publish(w, _article(w))
    weak = _publish(w, _article(w, device_model=False))
    draft = _article(w)
    with refused(w.env, ValidationError, "exactly one of"):
        Link.create({"article_id": art.id, "fault_code_id": w.fault.id, "brand_id": w.brand.id})
    with refused(w.env, ValidationError, "exactly one of"):
        Link.create({"article_id": art.id})
    with refused(w.env, ValidationError, "Relevance"):
        Link.create({"article_id": art.id, "fault_code_id": w.fault.id, "relevance_weight": 11})
    link = Link.create({"article_id": art.id, "fault_code_id": w.fault.id, "relevance_weight": 9})
    assert (link.link_type, link.linked_by_id) == ("fault", w.tech)
    with refused(w.env, ValidationError, "already linked"):
        Link.create({"article_id": art.id, "fault_code_id": w.fault.id})
    Link.create({"article_id": draft.id, "fault_code_id": w.fault.id})
    rows = (
        w.env["fix.knowledge.article"]
        .with_user(w.tech)
        .surface_for(fault_code_id=w.fault.id, device_model_id=w.model.id)
    )
    ids = [r["id"] for r in rows if r["kind"] == "article"]
    assert ids[0] == art.id  # the linked article first
    assert weak.id in ids  # brand-wide article of the job's brand
    assert draft.id not in ids  # only published content surfaces
    art.with_user(w.publisher).action_archive()
    with refused(w.env, ValidationError, "archived"):
        Link.create({"article_id": art.id, "brand_id": w.brand.id})
    with pytest.raises(AccessError):
        link.with_user(w.tech).unlink()


# ================================================================ page 5: offline sets
def test_an_offline_set_holds_published_in_scope_content_within_budget(w):
    Sets = w.env["fix.knowledge.offline.set"]
    in_scope = _publish(w, _article(w, rework_level="L2"))
    other_model = _publish(w, _article(w, device_model=w.model2.name))
    too_deep = _publish(w, _article(w, rework_level="L4"))
    not_offline = _publish(w, _article(w, offline_available=False))
    draft = _article(w)
    with pytest.raises(AccessError):
        Sets.with_user(w.tech).create({"user_id": w.tech.id, "budget_mb": 50})
    oset = Sets.with_user(w.publisher).create(
        {"user_id": w.tech.id, "budget_mb": 50, "max_level": "L2"}
    )
    with pytest.raises(UserError, match="Give .* its scope"):
        oset.with_user(w.publisher).action_compute()
    oset.with_user(w.publisher).write({"device_model_ids": [(6, 0, [w.model.id])]})
    with refused(w.env, ValidationError, "already has an offline set"):
        Sets.with_user(w.publisher).create({"user_id": w.tech.id, "budget_mb": 10})
    # the technician recomputes their own set; another technician cannot
    # (their own-set rule hides it from them altogether)
    with pytest.raises((AccessError, UserError)):
        oset.with_user(w.tech2).action_compute()
    oset.with_user(w.tech).action_compute()
    held = oset.article_ids
    assert in_scope in held
    for out in (other_model, too_deep, not_offline, draft):
        assert out not in held
    assert oset.total_mb > 0 and oset.computed_by_id == w.tech
    with pytest.raises(UserError, match=GUARD):
        oset.with_user(w.publisher).write({"article_ids": [(6, 0, [draft.id])]})
    # BRU-KMS-05: archiving takes it off every device
    in_scope.with_user(w.publisher).action_archive()
    assert in_scope not in oset.article_ids
    # the budget is a budget
    _publish(w, _article(w, rework_level="L1"))
    oset.with_user(w.publisher).write({"budget_mb": 0.0000001})
    oset.with_user(w.publisher).action_compute()
    assert not oset.article_ids and oset.over_budget_count >= 1
    # each technician sees their own set; only their device reports a sync
    assert not Sets.with_user(w.tech2).search([("id", "=", oset.id)])
    with pytest.raises(UserError, match="device syncs"):
        oset.with_user(w.publisher).action_mark_synced()
    oset.with_user(w.tech).action_mark_synced()
    assert oset.last_synced_on


# ================================================================ page 6: feedback
def test_feedback_is_given_once_on_published_content_and_kept(w):
    art = _article(w)
    Feedback = w.env["fix.knowledge.feedback"].with_user(w.tech)
    with pytest.raises(UserError, match="feedback is given on published content"):
        Feedback.create({"article_id": art.id, "resolved": "yes", "rating": 5})
    _publish(w, art)
    with pytest.raises(UserError, match=GUARD):
        Feedback.create(
            {"article_id": art.id, "resolved": "yes", "rating": 5, "user_id": w.tech2.id}
        )
    with refused(w.env, ValidationError, "1 to 5"):
        Feedback.create({"article_id": art.id, "resolved": "yes", "rating": 6})
    fb = Feedback.create(
        {"article_id": art.id, "resolved": "yes", "rating": 4, "comment": "worked"}
    )
    assert (fb.user_id, fb.version) == (w.tech, art.version)
    assert (art.helpful_votes, art.feedback_count, art.resolution_rate) == (1, 1, 100.0)
    with pytest.raises(UserError, match="already rated"):
        Feedback.create({"article_id": art.id, "resolved": "no", "rating": 1})
    with pytest.raises(UserError, match="kept as given"):
        fb.write({"rating": 1})
    with pytest.raises(AccessError):
        fb.unlink()
    w.env["fix.knowledge.feedback"].with_user(w.tech2).create(
        {"article_id": art.id, "resolved": "no", "rating": 2}
    )
    assert (art.feedback_count, art.resolution_rate, art.avg_rating) == (2, 50.0, 3.0)


def test_repeated_did_not_resolve_flags_the_article_until_revised(w):
    art = _publish(w, _article(w))
    for user in (w.tech, w.tech2, w.publisher2):
        w.env["fix.knowledge.feedback"].with_user(user).create(
            {"article_id": art.id, "resolved": "no", "rating": 2}
        )
    assert art.flagged_on and "did not resolve" in art.flag_reason
    owner_todo = w.env["mail.activity"].search(
        [("res_model", "=", art._name), ("res_id", "=", art.id), ("user_id", "=", w.author.id)]
    )
    assert owner_todo
    with pytest.raises(UserError, match=GUARD):
        art.with_user(w.author).write({"flagged_on": False})
    # the owner's revision answers the flag
    art.with_user(w.author).write({"content": "<p>Revised after feedback</p>"})
    assert not art.flagged_on


# ================================================================ reports and KPI
def test_the_usefulness_figures_come_from_feedback(w):
    m61 = pytest.importorskip("odoo.addons.cd_p03_portal.controllers.a10.m61")
    art = _publish(w, _article(w))
    w.env["fix.knowledge.feedback"].with_user(w.tech).create(
        {"article_id": art.id, "resolved": "yes", "rating": 5}
    )
    pack = m61.usage_usefulness(w.env)
    row = next(r for r in pack["rows"] if r["article"] == art.name[:60])
    assert (row["feedback"], row["resolved"], row["rating"]) == (1, 100.0, 5.0)
    assert m61.kpis(w.env)["usefulness_score"] > 0
    cap = (
        w.env["fix.knowledge.capture"]
        .with_user(w.tech)
        .create({"raw_text": "x", "device_brand": w.brand.name})
    )
    expertise = m61.expertise_map(w.env)
    people = {(r["brand"], r["person"]) for r in expertise["rows"]}
    assert (w.brand.name, w.author.name) in people
    assert (w.brand.name, cap.captured_by_id.name) in people
    assert all(r["risk"] == "CONCENTRATED" for r in expertise["rows"] if r["brand"] == w.brand.name)
