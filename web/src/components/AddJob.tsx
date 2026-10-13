import { useState } from "react";
import { tracked } from "@/lib/api";

export default function AddJob({ onAdded }: { onAdded: () => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [url, setUrl] = useState("");
  const [posted, setPosted] = useState("");
  const [state, setState] = useState("applied");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function reset() {
    setTitle("");
    setCompany("");
    setLocation("");
    setUrl("");
    setPosted("");
    setState("applied");
    setNotes("");
    setError("");
    setOpen(false);
  }

  async function save() {
    setSaving(true);
    setError("");
    let response: Response | null = null;
    try {
      response = await fetch("/api/manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          company,
          location,
          url,
          posted_at: posted,
          status: state,
          notes,
        }),
      });
    } catch {
      response = null;
    }
    setSaving(false);
    if (!response) {
      setError("Could not reach the server.");
      return;
    }
    if (!response.ok) {
      setError(
        response.status === 400
          ? "A title and a company are both required."
          : "Could not save that.",
      );
      return;
    }
    reset();
    onAdded();
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex h-[30px] shrink-0 items-center gap-1.5 rounded-control bg-accent px-3 text-[12.5px] font-medium text-white hover:bg-accent-hover"
      >
        <span className="text-[14px] leading-none">+</span>
        Add a job
      </button>
    );
  }

  return (
    <div className="mb-4 rounded-panel border border-line bg-surface p-5">
      <div className="text-[14px] font-semibold tracking-[-0.01em]">
        Add a job from outside
      </div>
      <p className="mt-1 text-[12.5px] text-text-3">
        A referral, a careers page, a recruiter email — anything that did not
        come through a source.
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Field
          label="Role"
          value={title}
          onChange={setTitle}
          placeholder="Software Engineer Intern"
        />
        <Field
          label="Company"
          value={company}
          onChange={setCompany}
          placeholder="Acme"
        />
        <Field
          label="Location"
          value={location}
          onChange={setLocation}
          placeholder="Boston, MA"
        />
        <Field
          label="Posted"
          value={posted}
          onChange={setPosted}
          placeholder="2026-10-12"
        />
        <div className="col-span-2">
          <Field
            label="Link"
            value={url}
            onChange={setUrl}
            placeholder="https://"
          />
        </div>
        <div className="col-span-2">
          <Field
            label="Notes"
            value={notes}
            onChange={setNotes}
            placeholder="Referred by a friend"
          />
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span className="text-[11px] font-medium tracking-[0.04em] text-text-5 uppercase">
          Status
        </span>
        {tracked.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setState(item.key)}
            className="flex h-[24px] items-center rounded-[11px] px-2.5 text-[12px] font-medium"
            style={{
              background: state === item.key ? item.bg : "transparent",
              color: state === item.key ? item.fg : "#6E6E73",
              border:
                state === item.key ? "none" : "1px solid var(--color-line)",
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="animate-in mt-3 text-[12.5px] text-[#B3261E]">
          {error}
        </div>
      ) : null}

      <div className="mt-5 flex items-center gap-2">
        <button
          type="button"
          onClick={save}
          disabled={saving || !title.trim() || !company.trim()}
          className="h-[30px] rounded-control bg-accent px-3.5 text-[13px] font-medium text-white hover:bg-accent-hover disabled:opacity-40"
        >
          {saving ? "Adding…" : "Add to tracker"}
        </button>
        <button
          type="button"
          onClick={reset}
          className="h-[30px] rounded-control border border-line px-3.5 text-[13px] font-medium text-text-2 hover:bg-hover"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (next: string) => void;
  placeholder: string;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[11px] font-medium tracking-[0.04em] text-text-5 uppercase">
        {label}
      </span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="h-[30px] rounded-control border border-line bg-surface px-2.5 text-[13px] outline-none"
      />
    </label>
  );
}
