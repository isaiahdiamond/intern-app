// The two shipped assets carry an image; the rest run on their gradient and
// are finished that way.
export const slots = {
  dashboard: {
    src: "/img/backdrop-dashboard.jpg",
    fallback:
      "radial-gradient(120% 90% at 18% -10%, #F2EFEA 0%, #FAFAFA 55%, #FAFAFA 100%)",
  },
  listings: {
    src: "",
    fallback:
      "radial-gradient(130% 100% at 80% -20%, #ECEFF2 0%, #FAFAFA 60%, #FAFAFA 100%)",
  },
  tracker: {
    src: "",
    fallback: "linear-gradient(165deg, #F3F0EC 0%, #FAFAFA 45%, #FAFAFA 100%)",
  },
  coach: {
    src: "",
    fallback: "linear-gradient(195deg, #EDEFF3 0%, #F6F5F4 50%, #FAFAFA 100%)",
  },
  profile: {
    src: "",
    fallback: "linear-gradient(180deg, #F5F3F0 0%, #FAFAFA 70%, #FAFAFA 100%)",
  },
  onboarding: {
    src: "",
    fallback:
      "radial-gradient(110% 80% at 50% -20%, #F0F4F6 0%, #FAFAFA 60%, #FAFAFA 100%)",
  },
};

export type Slot = keyof typeof slots;
