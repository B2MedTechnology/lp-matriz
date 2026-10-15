-- 0000 — o mínimo que a fila (0001) precisa num banco NOVO: um cadastro de clientes com dono (assessor).
-- Num banco que já tem `public.clientes`, este arquivo não muda nada (if not exists). A fila só usa id, nome e assessor.
create extension if not exists pgcrypto;
create table if not exists public.clientes (
  id       uuid primary key default gen_random_uuid(),
  nome     text not null,
  assessor text
);
comment on table public.clientes is
  'Cadastro mínimo de clientes para a fila da fábrica. Escrita: o painel · Leitura: lp_pedido_acao (0001). Retenção: permanente.';
alter table public.clientes enable row level security;
