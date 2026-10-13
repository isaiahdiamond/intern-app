import Layout from "@/components/Layout";

export default function Chat() {
  return (
    <Layout title="Coach">
      <div className="mx-auto flex max-w-[720px] flex-col items-center gap-[18px] py-16 text-center">
        <div className="text-[20px] font-semibold tracking-[-0.015em]">
          The coach is not built yet
        </div>
        <p className="m-0 max-w-[480px] text-[13.5px] leading-[1.55] text-text-3 text-pretty">
          This tab is a placeholder for a later phase. Nothing is wired to a
          model here, so there is no conversation to show. When it ships it will
          answer questions about the listings on your board, and every call will
          be logged.
        </p>
        <div className="box-border flex w-full max-w-[560px] items-center gap-2 rounded-[14px] border border-line-strong bg-surface px-3.5 py-2.5 opacity-50">
          <span className="flex-1 text-left text-[13.5px] text-text-4">
            Ask the coach anything
          </span>
          <div className="flex size-8 items-center justify-center rounded-[9px] bg-black/20 text-white">
            <svg
              width="14"
              height="14"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                d="M8 13V3M3.5 7.5L8 3l4.5 4.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
      </div>
    </Layout>
  );
}
