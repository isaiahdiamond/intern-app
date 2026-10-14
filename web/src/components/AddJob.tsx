import { useState } from "react";
import { tracked } from "@/lib/api";
import { paths } from "@/lib/icons";
import { Icon } from "./Icon";

export default function AddJob({
  onCancel,
  onAdded,
}: {
  onCancel: () => void;
  onAdded: () => void;
}) {
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
    onCancel();
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

  return (
    <div className="card mb-6 animate-in rounded-2xl p-6">
      <div className="text-section text-ink">Add a job from outside</div>
      <p className="mt-2 mb-0 text-body text-ink-3">
        A referral, a careers page, a recruiter email — anything that did not
        come through a source.
      </p>

      <div className="mt-5 grid grid-cols-2 gap-4">
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

      <div className="mt-5 flex flex-wrap items-center gap-2">
        <span className="mr-2 text-label text-ink-3 uppercase">Status</span>
        {tracked.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setState(item.key)}
            className="flex h-7 items-center rounded-full px-3 text-control"
            style={{
              background: state === item.key ? item.bg : "transparent",
              color: state === item.key ? item.fg : "var(--color-ink-3)",
              border:
                state === item.key
                  ? "1px solid transparent"
                  : "1px solid var(--color-line-strong)",
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="mt-4 flex animate-in items-center gap-2 rounded-md bg-[rgba(179,38,30,0.08)] px-3 py-2 text-body text-[#B3261E]">
          <Icon path={paths.warn} />
          {error}
        </div>
      ) : null}

      <div className="mt-6 flex items-center gap-2">
        <button
          type="button"
          onClick={save}
          disabled={saving || !title.trim() || !company.trim()}
          className="h-10 rounded-full bg-ink px-4 text-control text-ink-inverse transition-colors hover:bg-black disabled:cursor-not-allowed disabled:opacity-45 enabled:motion-safe:active:scale-[0.96]"
        >
          {saving ? "Adding…" : "Add to tracker"}
        </button>
        <button
          type="button"
          onClick={reset}
          className="h-10 rounded-full border border-line-strong bg-surface px-4 text-control text-ink hover:bg-hover"
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
    <label className="flex flex-col gap-2">
      <span className="text-label text-ink-3 uppercase">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="h-10 rounded-md border border-line bg-surface-sunk px-4 text-control text-ink outline-none"
      />
    </label>
  );
}
