# cd_front_desk — M04 Front Desk (P04-M02). The ext file extends all three
# base models AND defines fix.counter.sale, so it must import LAST.
# NOTE (parallel M25 session, 19:47): removed the nonexistent `fix_counter_sale`
# module from this import — per the comment above the model lives in
# fix_front_desk_ext. Restore if a dedicated file lands.
from . import fix_cash_shift, fix_front_desk_ext, fix_token_queue, fix_walkin_intake
