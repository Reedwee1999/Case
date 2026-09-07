SELECT 
    TRIM(tag) AS tag,
    COUNT(DISTINCT post_id) AS post_count,
    COUNT(*) AS total_usage
FROM (
    SELECT 
        post_id,
        UNNEST(tags) AS tag
    FROM {{ source('public', 'posts') }}
    WHERE tags IS NOT NULL AND array_length(tags, 1) > 0
) exploded_tags
GROUP BY TRIM(tag)
ORDER BY post_count DESC
