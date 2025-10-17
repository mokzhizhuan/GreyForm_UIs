// src/components/ModelSelection.tsx
import img6sides from '../assets/6sides_labelled_PBU.png';
import img4sides from '../assets/4sides_labelled_PBU.png';

type Props = {
  value: number | null;              // 4 or 6
  onChange: (v: number) => void;
};

const cards = [
  { title: "Model 1 (4 Walls)", img: img4sides, desc: "Choose this option if your IFC file contains a 4-walled room.", sides: 4 },
  { title: "Model 2 (6 Walls)", img: img6sides, desc: "Choose this option if your IFC file contains a 6-walled room.", sides: 6 },
];

export default function ModelSelection({ value, onChange }: Props) {
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex gap-4 py-4">
        {cards.map((card, idx) => {
          const selected = value === card.sides;
          return (
            <div key={idx} className="card bg-base-100 w-76 shadow-sm flex-shrink-0">
              <figure>
                <img src={card.img} alt={card.title} />
              </figure>
              <div className="card-body">
                <h2 className="card-title text-black">{card.title}</h2>
                <p className="text-black">{card.desc}</p>
                <div className="card-actions justify-center">
                  <button
                    className={`btn btn-primary ${selected ? "" : "btn-outline"}`}
                    onClick={() => onChange(card.sides)}
                  >
                    {selected ? "Selected" : "Select"}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
