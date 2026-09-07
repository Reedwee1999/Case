from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, to_timestamp, monotonically_increasing_id

# 1. Create Spark Session
spark = SparkSession.builder \
    .appName("SocialMediaETL") \
    .getOrCreate()

# 2. Read the JSON
df = spark.read.option("multiLine", "true").json("/home/jovyan/work/social_media_info.json")
print("JSON loaded")

# -------------------------------------------------------------------
# 3. Table: users
# -------------------------------------------------------------------
users = df.select(
    "user_id",
    "username",
    "email",
    "name",
    "age",
    "gender"
).dropDuplicates(["user_id"])

users.write \
    .mode("overwrite") \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres_warehouse:5432/warehouse") \
    .option("dbtable", "users") \
    .option("user", "warehouse") \
    .option("password", "warehouse") \
    .option("driver", "org.postgresql.Driver") \
    .save()
print("users table loaded")

# -------------------------------------------------------------------
# 4. Table: posts
# -------------------------------------------------------------------
df_posts_exploded = df.select(
    col("user_id"),
    explode(col("posts")).alias("post")
)

posts = df_posts_exploded.select(
    col("post.post_id").alias("post_id"),
    col("user_id"),
    col("post.post_text").alias("post_text"),
    col("post.location").alias("location"),
    to_timestamp(col("post.timestamp")).alias("timestamp"),
    col("post.shares").alias("shares"),
    col("post.reactions.like").alias("like_count"),
    col("post.reactions.love").alias("love_count"),
    col("post.reactions.wow").alias("wow_count"),
    col("post.reactions.haha").alias("haha_count"),
    col("post.reactions.sad").alias("sad_count"),
    col("post.reactions.angry").alias("angry_count"),
    col("post.tags").alias("tags")
).dropDuplicates(["post_id"])

posts.write \
    .mode("overwrite") \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres_warehouse:5432/warehouse") \
    .option("dbtable", "posts") \
    .option("user", "warehouse") \
    .option("password", "warehouse") \
    .option("driver", "org.postgresql.Driver") \
    .save()
print("posts table loaded")

# -------------------------------------------------------------------
# 5. Table: comments
# -------------------------------------------------------------------
comments = df_posts_exploded.select(
    col("post.post_id").alias("post_id"),
    col("user_id"),
    explode(col("post.comments")).alias("comment_struct")
).select(
    col("post_id"),
    col("user_id"),
    col("comment_struct.user_id").alias("commenter_user_id"),
    col("comment_struct.comment").alias("comment_text"),
    to_timestamp(col("comment_struct.timestamp")).alias("timestamp")
).withColumn("comment_id", monotonically_increasing_id())

comments.write \
    .mode("overwrite") \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres_warehouse:5432/warehouse") \
    .option("dbtable", "comments") \
    .option("user", "warehouse") \
    .option("password", "warehouse") \
    .option("driver", "org.postgresql.Driver") \
    .save()
print("comments table loaded")

print("All 3 tables loaded successfully")
