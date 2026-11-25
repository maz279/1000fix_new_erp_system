import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "1000FiX কাস্টমার পোর্টাল",
    short_name: "1000FiX",
    description:
      "সার্ভিস বুকিং, লাইভ ট্র্যাকিং, ডিভাইস ও সম্মতি — P01",
    start_url: "/",
    display: "standalone",
    background_color: "#fafafa",
    theme_color: "#0e7a6e",
    icons: [{ src: "/icon.svg", type: "image/svg+xml", sizes: "any" }],
  };
}
