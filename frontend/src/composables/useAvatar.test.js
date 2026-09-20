import { nextTick, ref } from "vue";
import { describe, expect, it, vi } from "vitest";

// Couvre useAvatar (2026-09-10, retour direct de l'utilisateur — "insérer sa
// photo"). URL.createObjectURL/revokeObjectURL n'existent pas dans jsdom :
// remplacées par des espions simples plutôt que d'ajouter une dépendance.

vi.mock("../services/api", () => ({
  default: { requete: vi.fn() },
}));

const { default: api } = await import("../services/api");
const { useAvatar } = await import("./useAvatar");

function poserFauxUrlObjet() {
  let compteur = 0;
  const cree = vi.fn(() => `blob:faux-${++compteur}`);
  const revoque = vi.fn();
  vi.stubGlobal("URL", { ...URL, createObjectURL: cree, revokeObjectURL: revoque });
  return { cree, revoque };
}

describe("useAvatar()", () => {
  it("ne charge rien tant qu'il n'y a ni utilisateur ni photo", async () => {
    poserFauxUrlObjet();
    const { url } = useAvatar(ref(null), ref(null));
    await nextTick();
    expect(url.value).toBeNull();
    expect(api.requete).not.toHaveBeenCalled();
  });

  it("charge la photo via la route authentifiée et expose une URL objet", async () => {
    const { cree } = poserFauxUrlObjet();
    const blob = new Blob(["contenu"]);
    api.requete.mockResolvedValueOnce({ blob: () => Promise.resolve(blob) });

    const { url } = useAvatar(ref(7), ref("avatars/abc.jpg"));
    await nextTick();
    await nextTick();

    expect(api.requete).toHaveBeenCalledWith("/api/v1/auth/utilisateurs/7/photo", { brut: true });
    expect(cree).toHaveBeenCalledWith(blob);
    expect(url.value).toBe("blob:faux-1");
  });

  it("recharge (et révoque l'ancienne URL) quand le chemin de la photo change", async () => {
    const { cree, revoque } = poserFauxUrlObjet();
    api.requete.mockResolvedValue({ blob: () => Promise.resolve(new Blob(["x"])) });

    const idUtilisateur = ref(7);
    const chemin = ref("avatars/premiere.jpg");
    const { url } = useAvatar(idUtilisateur, chemin);
    await nextTick();
    await nextTick();
    const premiereUrl = url.value;

    chemin.value = "avatars/seconde.jpg";
    await nextTick();
    await nextTick();

    expect(revoque).toHaveBeenCalledWith(premiereUrl);
    expect(cree).toHaveBeenCalledTimes(2);
  });

  it("retombe sur null (pas d'erreur) si la photo est introuvable", async () => {
    poserFauxUrlObjet();
    api.requete.mockRejectedValueOnce(new Error("404"));

    const { url } = useAvatar(ref(7), ref("avatars/absente.jpg"));
    await nextTick();
    await nextTick();

    expect(url.value).toBeNull();
  });
});
