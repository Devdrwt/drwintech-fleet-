import { redirect } from "next/navigation";

export default function Home() {
  // La carte est l'écran d'accueil ; le layout protégé renvoie vers /login
  // si aucun token n'est présent.
  redirect("/map");
}
