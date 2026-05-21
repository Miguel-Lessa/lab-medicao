-- Lab04S01 - Caracterizacao do dataset YouTube Research
-- Conexao Power BI:
-- Servidor: localhost:55432
-- Banco: youtube_research
-- Usuario: yt
-- Senha: ytsecret

-- 1. Cartoes de volume geral
SELECT 'Linguagens' AS metrica, count(*)::bigint AS valor FROM language
UNION ALL SELECT 'Consultas de busca', count(*) FROM search_query
UNION ALL SELECT 'Execucoes de busca', count(*) FROM search_run
UNION ALL SELECT 'Canais', count(*) FROM channel
UNION ALL SELECT 'Playlists', count(*) FROM playlist
UNION ALL SELECT 'Videos', count(*) FROM video
UNION ALL SELECT 'Comentarios', count(*) FROM video_comment;

-- 2. Playlists e canais por linguagem
SELECT
  l.name AS linguagem,
  l.slug,
  count(p.playlist_id)::bigint AS playlists,
  count(DISTINCT p.owner_channel_id)::bigint AS canais
FROM language l
LEFT JOIN playlist p ON p.language_id = l.id
GROUP BY l.id, l.name, l.slug
ORDER BY playlists DESC;

-- 3. Status do filtro de playlists
SELECT
  coalesce(filter_status, 'SEM_STATUS') AS status_filtro,
  count(*)::bigint AS playlists,
  round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS percentual
FROM playlist
GROUP BY coalesce(filter_status, 'SEM_STATUS')
ORDER BY playlists DESC;

-- 4. Status do filtro por linguagem
SELECT
  l.name AS linguagem,
  coalesce(p.filter_status, 'SEM_STATUS') AS status_filtro,
  count(*)::bigint AS playlists
FROM playlist p
JOIN language l ON l.id = p.language_id
GROUP BY l.name, coalesce(p.filter_status, 'SEM_STATUS')
ORDER BY l.name, playlists DESC;

-- 5. Playlists por ano de publicacao
SELECT
  extract(year from published_at)::int AS ano_publicacao,
  count(*)::bigint AS playlists
FROM playlist
WHERE published_at IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 6. Playlists descobertas por dia de coleta
SELECT
  date(discovered_at) AS dia_coleta,
  count(*)::bigint AS playlists_descobertas
FROM playlist
WHERE discovered_at IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 7. Execucoes de busca por status
SELECT
  status,
  count(*)::bigint AS execucoes,
  sum(coalesce(items_returned, 0))::bigint AS itens_retornados,
  sum(coalesce(quota_cost, 0))::bigint AS custo_quota,
  round(avg(coalesce(items_returned, 0))::numeric, 2) AS media_itens_por_execucao
FROM search_run
GROUP BY status
ORDER BY execucoes DESC;

-- 8. Consultas e execucoes por linguagem
SELECT
  l.name AS linguagem,
  count(DISTINCT sq.id)::bigint AS consultas,
  count(sr.id)::bigint AS execucoes,
  sum(coalesce(sr.items_returned, 0))::bigint AS itens_retornados,
  sum(coalesce(sr.quota_cost, 0))::bigint AS custo_quota
FROM language l
LEFT JOIN search_query sq ON sq.language_id = l.id
LEFT JOIN search_run sr ON sr.query_id = sq.id
GROUP BY l.id, l.name
ORDER BY execucoes DESC;

-- 9. Top canais por quantidade de playlists
SELECT
  c.title AS canal,
  count(p.playlist_id)::bigint AS playlists,
  count(DISTINCT p.language_id)::bigint AS linguagens
FROM channel c
JOIN playlist p ON p.owner_channel_id = c.channel_id
GROUP BY c.channel_id, c.title
ORDER BY playlists DESC
LIMIT 10;

-- 10. Completude dos campos principais
SELECT 'channel.subscriber_count' AS campo, count(*) AS total, count(subscriber_count) AS preenchidos, count(*) - count(subscriber_count) AS ausentes FROM channel
UNION ALL SELECT 'channel.country', count(*), count(country), count(*) - count(country) FROM channel
UNION ALL SELECT 'channel.title', count(*), count(title), count(*) - count(title) FROM channel
UNION ALL SELECT 'playlist.item_count', count(*), count(item_count), count(*) - count(item_count) FROM playlist
UNION ALL SELECT 'playlist.title', count(*), count(title), count(*) - count(title) FROM playlist
UNION ALL SELECT 'playlist.published_at', count(*), count(published_at), count(*) - count(published_at) FROM playlist;
