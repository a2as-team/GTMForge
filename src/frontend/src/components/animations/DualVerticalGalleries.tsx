import VerticalGallery from "./VerticalGallery";

export default function DualVerticalGalleries() {
  return (
    <>
      <VerticalGallery
        items={leftItems}
        widthClass="w-[280px] left-0"
        itemSize={200}
        speedMs={45000}
        direction="down"
        className="opacity-100"
      />

      <VerticalGallery
        items={rightItems}
        widthClass="w-[280px] right-0"
        itemSize={200}
        speedMs={40000}
        direction="up"
        className="opacity-100"
      />
    </>
  );
}

const leftItems = [
  { id: 1,  src: "/images/greenleaf.jpg",    alt: "GreenLeaf" },
  { id: 2,  src: "/images/onboardOS.jpg",    alt: "OnboardOS" },
  { id: 3,  src: "/images/relay.jpg",        alt: "Relay" },
  { id: 4,  src: "/images/knighthacks.jpg",  alt: "KnightHacks" },
  { id: 5,  src: "/images/shadowhire.jpg",   alt: "Shadowhire" },
  { id: 6,  src: "/images/knightmentor.jpg", alt: "KnightMentor" },
  { id: 7,  src: "/images/ledgerless.jpg",   alt: "Ledgerless" },
  { id: 8,  src: "/images/orbit.jpg",        alt: "Orbit" },
  { id: 9,  src: "/images/atlaspitch.jpg",   alt: "AtlasPitch" },
  { id: 10, src: "/images/ecotracker.jpg",   alt: "EcoTracker" },
  { id: 11, src: "/images/synclayer.jpg",    alt: "Ledgerless" },
  { id: 12, src: "/images/pawporter.jpg",    alt: "PawPorter" },
  { id: 13, src: "/images/composer.jpg",     alt: "Composer" },
  { id: 14, src: "/images/ixmyride.jpg",     alt: "IxMyRide" },
  { id: 15, src: "/images/queuequest.jpg",   alt: "QueueQuest" },
  { id: 16, src: "/images/musemap.jpg",      alt: "MuseMap" },
];

const rightItems = [
  { id: 17, src: "/images/knighthacks.jpg",  alt: "KnightHacks" },
  { id: 18, src: "/images/relay.jpg",        alt: "Relay" },
  { id: 19, src: "/images/onboardOS.jpg",    alt: "OnboardOS" },
  { id: 20, src: "/images/ecotracker.jpg",   alt: "EcoTracker" },
  { id: 21, src: "/images/pawporter.jpg",    alt: "PawPorter" },
  { id: 22, src: "/images/atlaspitch.jpg",   alt: "AtlasPitch" },
  { id: 23, src: "/images/synclayer.jpg",   alt: "SyncLayer" },
  { id: 24, src: "/images/composer.jpg",     alt: "Composer" },
  { id: 25, src: "/images/queuequest.jpg",    alt: "QueueQuest" },
  { id: 26, src: "/images/ixmyride.jpg",     alt: "IxMyRide" },
  { id: 27, src: "/images/ledgerless.jpg",   alt: "Ledgerless" },
  { id: 28, src: "/images/musemap.jpg",      alt: "MuseMap" },
  { id: 29, src: "/images/knightmentor.jpg", alt: "KnightMentor" },
  { id: 30, src: "/images/shadowhire.jpg",   alt: "Shadowhire" },
  { id: 31, src: "/images/greenleaf.jpg",    alt: "GreenLeaf" },
  { id: 32, src: "/images/orbit.jpg",        alt: "Orbit" },
];



