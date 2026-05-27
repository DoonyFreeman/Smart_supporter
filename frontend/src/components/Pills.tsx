interface Props {
  value: string;
  kind: 'status' | 'priority' | 'tag';
}

export function Pill({ value, kind }: Props) {
  const cls = kind === 'tag' ? 'pill tag' : `pill ${kind}-${value}`;
  const label = value.replace('_', ' ');
  return <span className={cls}>{label}</span>;
}
