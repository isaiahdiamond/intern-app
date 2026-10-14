export type Listing = {
  id: number;
  title: string;
  company: string;
  location: string;
  url: string;
  posted_at: string;
  source: string;
  full_text: number;
  first_seen: string;
  copies: number;
  display_title: string;
  level: string;
  education: string;
  term: string;
  citizenship: string;
  years_experience: number;
  industry: string;
  has_icon: number;
  industry_rank: number;
  status: string;
  notes: string;
  status_changed_at: string | null;
  days_in_status: number | null;
};

export type HistoryEntry = { status: string; changed_at: string };

export type Tracked = Listing & { history: HistoryEntry[] };

export type Page = {
  listings: Listing[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
};

export type Filters = {
  industries: string[];
  industry_counts: Record<string, number>;
  status_counts: Record<string, number>;
  level_counts: Record<string, number>;
  education_counts: Record<string, number>;
  board_status_counts: Record<string, number>;
  roles: string[];
  sorts: string[];
  statuses: string[];
};

export type Profile = {
  onboarded: boolean;
  profile: {
    school: string;
    major: string;
    education: string;
    seeking: string[];
    roles: string[];
    industries: string[];
    created_at: string;
    updated_at: string;
  } | null;
};

export type StatusKey =
  | "new"
  | "saved"
  | "applied"
  | "interviewing"
  | "offer"
  | "rejected"
  | "hidden";

export const statuses: {
  key: StatusKey;
  label: string;
  fg: string;
  bg: string;
  dot: string;
}[] = [
  {
    key: "new",
    label: "New",
    fg: "#171717",
    bg: "rgba(23,23,23,0.07)",
    dot: "#171717",
  },
  {
    key: "saved",
    label: "Saved",
    fg: "#9A5400",
    bg: "rgba(255,149,0,0.13)",
    dot: "#FF9500",
  },
  {
    key: "applied",
    label: "Applied",
    fg: "#1E7A34",
    bg: "rgba(52,199,89,0.14)",
    dot: "#34C759",
  },
  {
    key: "interviewing",
    label: "Interviewing",
    fg: "#7A3DA8",
    bg: "rgba(175,82,222,0.12)",
    dot: "#AF52DE",
  },
  {
    key: "offer",
    label: "Offer",
    fg: "#0B6E80",
    bg: "rgba(48,176,199,0.15)",
    dot: "#30B0C7",
  },
  {
    key: "rejected",
    label: "Rejected",
    fg: "#666666",
    bg: "rgba(23,23,23,0.05)",
    dot: "#AEAEB2",
  },
  {
    key: "hidden",
    label: "Ignored",
    fg: "#8A8A8A",
    bg: "rgba(23,23,23,0.04)",
    dot: "#C7C7CC",
  },
];

const unknown = {
  key: "new" as StatusKey,
  label: "Unknown",
  fg: "#666666",
  bg: "rgba(23,23,23,0.05)",
  dot: "#AEAEB2",
};

// Everything the tracker holds, in the order a search moves through them.
// Ignored is not one of them: it is the shelf a listing goes to instead.
export const tracked = statuses.filter(
  (status) => status.key !== "new" && status.key !== "hidden",
);

export function status(key: string) {
  return statuses.find((item) => item.key === key) ?? unknown;
}

export function trackedTotal(counts: Record<string, number>) {
  let total = 0;
  for (const item of tracked) total += counts[item.key] ?? 0;
  return total;
}

export async function get<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path);
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function saveStatus(id: number, next: string) {
  try {
    const response = await fetch("/api/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ listing_id: id, status: next }),
    });
    if (!response.ok) return null;
    return (await response.json()) as {
      counts: Record<string, number>;
      board_counts: Record<string, number>;
    };
  } catch {
    return null;
  }
}

export function ago(iso: string) {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const hours = Math.floor((Date.now() - date.getTime()) / 3600000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  if (hours < 24 * 7) return `${Math.floor(hours / 24)}d ago`;
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function fullDate(iso: string) {
  if (!iso) return "unknown";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function today() {
  const now = new Date();
  const day = now
    .toLocaleDateString("en-US", { weekday: "short" })
    .toLowerCase();
  const date = now
    .toLocaleDateString("en-US", { month: "short", day: "numeric" })
    .toLowerCase();
  return `${day} · ${date}`;
}

// What a listing says about itself beyond its title. Citizenship and years of
// experience come only from the posting body, so they show on the listings whose
// full text we hold and are absent on the rest.
export function titleTags(listing: Listing) {
  const labels: Record<string, string> = {
    intern: "Intern",
    coop: "Co-op",
    new_grad: "New grad",
    other: "Other",
    undergrad: "Undergrad",
    masters: "Masters",
    phd: "PhD",
    any: "Any degree",
    us_citizen: "US citizens",
    clearance: "Clearance",
    no_sponsorship: "No sponsorship",
  };
  const tags = [];
  if (listing.level) tags.push(labels[listing.level] ?? listing.level);
  if (listing.education)
    tags.push(labels[listing.education] ?? listing.education);
  if (listing.term) tags.push(listing.term);
  if (listing.citizenship)
    tags.push(labels[listing.citizenship] ?? listing.citizenship);
  if (listing.years_experience > 0)
    tags.push(`${listing.years_experience}+ yrs`);
  return tags;
}

export function monthKey() {
  return new Date().toISOString().slice(0, 7);
}

export function lastDays(count: number) {
  const days = [];
  for (let back = count - 1; back >= 0; back -= 1) {
    const date = new Date();
    date.setDate(date.getDate() - back);
    days.push({ key: date.toISOString().slice(0, 10), date, count: 0 });
  }
  return days;
}
