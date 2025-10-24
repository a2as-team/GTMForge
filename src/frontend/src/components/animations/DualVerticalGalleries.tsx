import VerticalGallery from "./VerticalGallery";

export default function DualVerticalGalleries() {
  return (
    <>
      {/* Left Gallery - full height, manual + auto scroll down */}
      <VerticalGallery
        items={leftItems}
        widthClass="w-[260px] left-0"
        itemSize={150}
        speedMs={45000}
        direction="down"
        className="opacity-100"
      />

      {/* Right Gallery - full height, manual + auto scroll up */}
      <VerticalGallery
        items={rightItems}
        widthClass="w-[260px] right-0"
        itemSize={150}
        speedMs={40000}
        direction="up"
        className="opacity-100"
      />
    </>
  );
}

const leftItems = [
  { id: 1, src: "https://picsum.photos/seed/left1/800/800", alt: "SaaS Launch" },
  { id: 2, src: "https://picsum.photos/seed/left2/800/800", alt: "Product Strategy" },
  { id: 3, src: "https://picsum.photos/seed/left3/800/800", alt: "Market Entry" },
  { id: 4, src: "https://picsum.photos/seed/left4/800/800", alt: "Growth Hacking" },
  { id: 5, src: "https://picsum.photos/seed/left5/800/800", alt: "B2B Marketing" },
  { id: 6, src: "https://picsum.photos/seed/left6/800/800", alt: "Channel Strategy" },
  { id: 7, src: "https://picsum.photos/seed/left7/800/800", alt: "Pricing Model" },
  { id: 8, src: "https://picsum.photos/seed/left8/800/800", alt: "Customer Acquisition" },
  { id: 9, src: "https://picsum.photos/seed/left9/800/800", alt: "Brand Positioning" },
  { id: 10, src: "https://picsum.photos/seed/left10/800/800", alt: "Product-Market Fit" },
  { id: 11, src: "https://picsum.photos/seed/left11/800/800", alt: "Competitive Analysis" },
  { id: 12, src: "https://picsum.photos/seed/left12/800/800", alt: "Sales Funnel" },
  { id: 13, src: "https://picsum.photos/seed/left13/800/800", alt: "Retention Strategy" },
  { id: 14, src: "https://picsum.photos/seed/left14/800/800", alt: "Market Segmentation" },
  { id: 15, src: "https://picsum.photos/seed/left15/800/800", alt: "Value Proposition" },
  { id: 16, src: "https://picsum.photos/seed/left16/800/800", alt: "User Onboarding" },
  { id: 17, src: "https://picsum.photos/seed/left17/800/800", alt: "Content Marketing" },
  { id: 18, src: "https://picsum.photos/seed/left18/800/800", alt: "Partnership Strategy" },
  { id: 19, src: "https://picsum.photos/seed/left19/800/800", alt: "Revenue Model" },
  { id: 20, src: "https://picsum.photos/seed/left20/800/800", alt: "Launch Timeline" },
];

const rightItems = [
  { id: 'a', src: "https://picsum.photos/seed/rightA/800/800", alt: "Digital Transformation" },
  { id: 'b', src: "https://picsum.photos/seed/rightB/800/800", alt: "Enterprise Sales" },
  { id: 'c', src: "https://picsum.photos/seed/rightC/800/800", alt: "MVP Strategy" },
  { id: 'd', src: "https://picsum.photos/seed/rightD/800/800", alt: "Market Validation" },
  { id: 'e', src: "https://picsum.photos/seed/rightE/800/800", alt: "Startup Metrics" },
  { id: 'f', src: "https://picsum.photos/seed/rightF/800/800", alt: "Lead Generation" },
  { id: 'g', src: "https://picsum.photos/seed/rightG/800/800", alt: "Community Building" },
  { id: 'h', src: "https://picsum.photos/seed/rightH/800/800", alt: "Product Demo" },
  { id: 'i', src: "https://picsum.photos/seed/rightI/800/800", alt: "Market Research" },
  { id: 'j', src: "https://picsum.photos/seed/rightJ/800/800", alt: "Pitch Deck" },
  { id: 'k', src: "https://picsum.photos/seed/rightK/800/800", alt: "Unit Economics" },
  { id: 'l', src: "https://picsum.photos/seed/rightL/800/800", alt: "User Personas" },
  { id: 'm', src: "https://picsum.photos/seed/rightM/800/800", alt: "PLG Strategy" },
  { id: 'n', src: "https://picsum.photos/seed/rightN/800/800", alt: "Market Trends" },
  { id: 'o', src: "https://picsum.photos/seed/rightO/800/800", alt: "Conversion Optimization" },
  { id: 'p', src: "https://picsum.photos/seed/rightP/800/800", alt: "Brand Voice" },
  { id: 'q', src: "https://picsum.photos/seed/rightQ/800/800", alt: "Referral Program" },
  { id: 'r', src: "https://picsum.photos/seed/rightR/800/800", alt: "Customer Journey" },
  { id: 's', src: "https://picsum.photos/seed/rightS/800/800", alt: "Market Expansion" },
  { id: 't', src: "https://picsum.photos/seed/rightT/800/800", alt: "Investor Relations" },
];


