SELECT 
    u.user_id,
    u.username,
    u.name,
    u.age,
    u.gender,
    COUNT(DISTINCT p.post_id) AS total_posts,
    SUM(p.shares) AS total_shares,
    SUM(p.like_count + p.love_count + p.wow_count + p.haha_count + p.sad_count + p.angry_count) AS total_reactions
FROM {{ source('public', 'users') }} u
LEFT JOIN {{ source('public', 'posts') }} p ON u.user_id = p.user_id
GROUP BY u.user_id, u.username, u.name, u.age, u.gender
