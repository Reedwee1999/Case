SELECT 
    p.post_id,
    p.user_id,
    p.post_text,
    p.location,
    p.timestamp,
    p.shares,
    (p.like_count + p.love_count + p.wow_count + p.haha_count + p.sad_count + p.angry_count) AS total_reactions,
    COUNT(c.comment_id) AS total_comments,
    (p.like_count + p.love_count + p.wow_count + p.haha_count + p.sad_count + p.angry_count + p.shares + COUNT(c.comment_id)) AS total_engagement_score
FROM {{ source('public', 'posts') }} p
LEFT JOIN {{ source('public', 'comments') }} c ON p.post_id = c.post_id
GROUP BY p.post_id, p.user_id, p.post_text, p.location, p.timestamp, p.shares, p.like_count, p.love_count, p.wow_count, p.haha_count, p.sad_count, p.angry_count
