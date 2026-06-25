export interface SourceMeta {
  label: string
  color: string
  key: string
  bg: string
}

const SOURCE_META: Record<string, SourceMeta> = {
  hackernews: { label: 'HN', color: 'var(--hn)', key: 'hn', bg: 'rgba(224,93,0,0.08)' },
  openai: { label: 'OpenAI', color: 'var(--openai)', key: 'openai', bg: 'rgba(13,138,106,0.08)' },
  google_ai: { label: 'Google AI', color: 'var(--google)', key: 'google', bg: 'rgba(26,115,232,0.08)' },
  mit: { label: 'MIT', color: 'var(--mit-fg)', key: 'mit', bg: 'rgba(155,28,46,0.08)' },
  huggingface: { label: 'Hugging Face', color: '#FF9D00', key: 'hf', bg: 'rgba(255,157,0,0.10)' },
  techcrunch_ai: { label: 'TechCrunch AI', color: '#00A562', key: 'tc', bg: 'rgba(0,165,98,0.10)' },
  arxiv_ai: { label: 'arXiv AI', color: '#B31B1B', key: 'arxiv', bg: 'rgba(179,27,27,0.10)' },
  reddit_ml: { label: 'Reddit ML', color: '#FF4500', key: 'reddit', bg: 'rgba(255,69,0,0.10)' },
  github_ai: { label: 'GitHub AI', color: '#57606A', key: 'github', bg: 'rgba(87,96,106,0.10)' },
  github_trending: { label: 'GitHub', color: '#57606A', key: 'github', bg: 'rgba(87,96,106,0.10)' },
  infoq_cn: { label: 'InfoQ 中文', color: '#2563EB', key: 'infoq', bg: 'rgba(37,99,235,0.10)' },
  machine_heart: { label: '机器之心', color: '#8B5CF6', key: 'jqr', bg: 'rgba(139,92,246,0.10)' },
  qbitai: { label: '量子位', color: '#0EA5E9', key: 'qbit', bg: 'rgba(14,165,233,0.10)' },
}

export function sourceMeta(source?: string | null): SourceMeta {
  if (!source) return { label: '?', color: 'var(--brand)', key: 'default', bg: 'var(--bg-elevated)' }
  return SOURCE_META[source] || { label: source, color: 'var(--brand)', key: source, bg: 'var(--bg-elevated)' }
}
