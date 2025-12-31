import { type FC } from 'react';

export const Dashboard: FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-2">
          Benvenuto in FLUXION - Il tuo gestionale enterprise
        </p>
      </div>

      {/* Placeholder content */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:scale-105 transition-transform"
          >
            <p className="text-sm text-slate-400">KPI {i}</p>
            <p className="text-3xl font-bold text-white mt-2">--</p>
          </div>
        ))}
      </div>
    </div>
  );
};
