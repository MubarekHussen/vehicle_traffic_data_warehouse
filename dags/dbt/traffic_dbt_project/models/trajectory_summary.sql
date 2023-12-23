WITH track_summary AS (
    SELECT
        track_id,
        type,
        SUM(traveled_d) AS total_distance,
        AVG(avg_speed) AS average_speed
    FROM {{ ref('trajectory_info') }}
    GROUP BY track_id, type
)

SELECT *
FROM track_summary;
