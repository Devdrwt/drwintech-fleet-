"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { billingApi } from "@/lib/api/endpoints";

interface Invoice {
  id: number;
  number: string;
  amount: string;
  currency: string;
  status: string;
  due_date: string | null;
}

export default function FacturesPage() {
  const [paying, setPaying] = useState<number | null>(null);
  const { data, isLoading } = useQuery({
    queryKey: ["client", "invoices"],
    queryFn: () => billingApi.invoices().then((r) => r.data),
  });
  const invoices: Invoice[] = data?.results ?? data ?? [];

  async function pay(id: number) {
    setPaying(id);
    try {
      const { data } = await billingApi.pay(id);
      if (data?.payment_url) window.location.href = data.payment_url;
    } catch {
      alert("Paiement indisponible pour le moment.");
    } finally {
      setPaying(null);
    }
  }

  async function downloadPdf(id: number) {
    try {
      const { data } = await billingApi.invoicePdf(id);
      const url = URL.createObjectURL(data as Blob);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch {
      alert("PDF indisponible.");
    }
  }

  return (
    <div className="p-4 space-y-3">
      <h1 className="text-lg font-semibold text-gray-900">Factures</h1>
      {isLoading && <p className="text-gray-500">Chargement...</p>}
      {!isLoading && invoices.length === 0 && (
        <p className="text-gray-400 text-sm">Aucune facture.</p>
      )}
      {invoices.map((inv) => {
        const unpaid = inv.status !== "paid";
        return (
          <div key={inv.id} className="bg-white rounded-xl shadow p-3">
            <div className="flex justify-between items-center">
              <span className="font-medium text-gray-800">{inv.number}</span>
              <span className="text-gray-900 font-semibold">
                {inv.amount} {inv.currency}
              </span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  unpaid ? "bg-amber-100 text-amber-700" : "bg-green-100 text-green-700"
                }`}
              >
                {inv.status}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => downloadPdf(inv.id)}
                  className="border border-gray-300 text-gray-700 rounded-lg px-3 py-1 text-sm"
                >
                  PDF
                </button>
                {unpaid && (
                  <button
                    onClick={() => pay(inv.id)}
                    disabled={paying === inv.id}
                    className="bg-primary text-white rounded-lg px-3 py-1 text-sm disabled:opacity-60"
                  >
                    {paying === inv.id ? "..." : "Payer"}
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
