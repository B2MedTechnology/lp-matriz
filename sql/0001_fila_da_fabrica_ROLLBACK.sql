-- ROLLBACK 0001 — fábrica de landing pages (as prévias já publicadas na Vercel ficam lá)
begin;
drop function if exists public.lp_pedido_pegar();
drop function if exists public.lp_config_salvar(text, jsonb);
drop function if exists public.lp_pedido_acao(text, text, boolean, bigint, jsonb);
drop function if exists public.lp_pedidos_list(text);
drop function if exists public.lp_config_ver();
drop table if exists public.lp_pedidos;
drop table if exists public.lp_config;
commit;
