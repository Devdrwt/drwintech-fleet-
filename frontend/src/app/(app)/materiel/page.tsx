"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fleetApi } from "@/lib/api/endpoints";

interface Unit {
  id: number;
  imei: string;
  brand: string;
  model_name: string;
  status: string;
  traccar_device_id: number | null;
}

export default function MaterielPage() {
  const qc = useQueryClient();
  const [imei, setImei] = useState("");
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["units"],
    queryFn: () => fleetApi.units().then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: () =>
      fleetApi.createUnit({ imei, brand, model_name: model }),
    onSuccess: () => {
      setImei("");
      setBrand("");
      setModel("");
      setError(null);
      qc.invalidateQueries({ queryKey: ["units"] });
    },
    onError: () => setError("Échec (IMEI déjà existant ?)."),
  });

  const units: Unit[] = data?.results ?? data ?? [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">Matériel (balises GPS)</h1>
      <p className="text-sm text-gray-500">
        La création d&apos;une balise provisionne automatiquement le device sur le
        moteur Traccar (colonne « Device Traccar »).
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (imei) create.mutate();
        }}
        className="bg-white rounded-xl shadow p-4 flex flex-wrap gap-3 items-end"
      >
        <Field label="IMEI" value={imei} onChange={setImei} />
        <Field label="Marque" value={brand} onChange={setBrand} />
        <Field label="Modèle" value={model} onChange={setModel} />
        <button
          type="submit"
          disabled={create.isPending}
          className="bg-primary text-white rounded-lg px-4 py-2 text-sm disabled:opacity-60"
        >
          {create.isPending ? "Création..." : "Créer + provisionner"}
        </button>
        {error && <span className="text-sm text-red-600">{error}</span>}
      </form>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        {isLoading ? (
          <p className="p-4 text-gray-500">Chargement...</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-2">IMEI</th>
                <th className="px-4 py-2">Marque</th>
                <th className="px-4 py-2">Modèle</th>
                <th className="px-4 py-2">Statut</th>
                <th className="px-4 py-2">Device Traccar</th>
              </tr>
            </thead>
            <tbody>
              {units.map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="px-4 py-2 font-mono">{u.imei}</td>
                  <td className="px-4 py-2">{u.brand}</td>
                  <td className="px-4 py-2">{u.model_name}</td>
                  <td className="px-4 py-2">{u.status}</td>
                  <td className="px-4 py-2">
                    {u.traccar_device_id ?? (
                      <span className="text-amber-600">non provisionné</span>
                    )}
                  </td>
                </tr>
              ))}
              {units.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-gray-400">
                    Aucune balise.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-gray-500">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block border rounded-lg px-3 py-2 text-sm"
      />
    </div>
  );
}
