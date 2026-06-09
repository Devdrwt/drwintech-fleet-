"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { clientsApi } from "@/lib/api/endpoints";

interface Client {
  id: number;
  name: string;
  client_type: string;
  status: string;
  email: string;
  phone: string;
  city: string;
  country: string;
}

export default function ClientsPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: () => clientsApi.list().then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: () =>
      clientsApi.create({ name, email, phone, client_type: "company" }),
    onSuccess: () => {
      setName("");
      setEmail("");
      setPhone("");
      qc.invalidateQueries({ queryKey: ["clients"] });
    },
  });

  const clients: Client[] = data?.results ?? data ?? [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">Clients</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (name) create.mutate();
        }}
        className="bg-white rounded-xl shadow p-4 flex flex-wrap gap-3 items-end"
      >
        <Field label="Nom" value={name} onChange={setName} />
        <Field label="Email" value={email} onChange={setEmail} />
        <Field label="Téléphone" value={phone} onChange={setPhone} />
        <button
          type="submit"
          disabled={create.isPending}
          className="bg-primary text-white rounded-lg px-4 py-2 text-sm disabled:opacity-60"
        >
          {create.isPending ? "Ajout..." : "Ajouter"}
        </button>
      </form>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        {isLoading ? (
          <p className="p-4 text-gray-500">Chargement...</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-2">Nom</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Statut</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Téléphone</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="px-4 py-2">{c.name}</td>
                  <td className="px-4 py-2">{c.client_type}</td>
                  <td className="px-4 py-2">{c.status}</td>
                  <td className="px-4 py-2">{c.email}</td>
                  <td className="px-4 py-2">{c.phone}</td>
                </tr>
              ))}
              {clients.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-gray-400">
                    Aucun client.
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
