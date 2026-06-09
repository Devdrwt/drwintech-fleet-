"use client";

import Link from "next/link";
import { CheckCircle } from "lucide-react";

export default function PaiementRetourPage() {
  return (
    <div className="p-6 flex flex-col items-center text-center gap-4 mt-10">
      <CheckCircle size={56} className="text-green-500" />
      <h1 className="text-lg font-semibold text-gray-900">Paiement initié</h1>
      <p className="text-sm text-gray-500">
        Votre paiement est en cours de traitement. Le statut de la facture sera
        mis à jour dès confirmation de l&apos;agrégateur.
      </p>
      <Link
        href="/client/factures"
        className="bg-primary text-white rounded-lg px-4 py-2 text-sm"
      >
        Retour aux factures
      </Link>
    </div>
  );
}
