import Layout from "@/components/Layout";

export default function Chat() {
  return (
    <Layout title="Coach" subtitle="A later phase." slot="coach">
      <div className="card mx-auto flex max-w-[720px] flex-col items-center gap-6 rounded-2xl px-8 py-12 text-center">
        <div
          className="image-outline h-60 w-80 rounded-md"
          style={{
            background: "linear-gradient(135deg, #EFEFEF 0%, #E4E4E4 100%)",
          }}
        />
        <div className="text-section text-ink">The coach is not built yet</div>
        <p className="m-0 max-w-[480px] text-lead text-ink-2 text-pretty">
          This tab is a placeholder for a later phase. Nothing is wired to a
          model here, so there is no conversation to show. When it ships it will
          answer questions about the listings on your board, and every call will
          be logged.
        </p>
      </div>
    </Layout>
  );
}
