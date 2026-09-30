"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError, type PublicProof } from "@/lib/api";
import { clearPrefs } from "@/lib/prefs";
import ProofStatement from "@/components/ProofStatement";
import { Button, Loading } from "@/components/ui";

/** Public landlord view (screen 11). No navigation to the rest of the app. */
export default function LandlordView() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const [proof, setProof] = useState<PublicProof | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    api<PublicProof>(`/proofs/${encodeURIComponent(token)}`)
      .then(setProof)
      .catch((e) => (e instanceof ApiError && e.status === 404 ? setNotFound(true) : setProof({ state: "invalid", checked: "" })));
  }, [token]);

  async function restart() {
    try {
      await api("/session", { method: "DELETE" });
    } catch {}
    clearPrefs();
    router.push("/");
  }

  if (notFound) return <ProofStatement state="invalid" checked="" />;
  if (!proof) return <div className="px-5 pt-5"><Loading label="Checking signature…" /></div>;
  return (
    <ProofStatement state={proof.state} checked={proof.checked} snapshot={proof.snapshot}
      footer={process.env.NEXT_PUBLIC_DEMO_MODE !== "false" && (
        <Button variant="secondary" onClick={restart}>Restart demo</Button>
      )} />
  );
}
