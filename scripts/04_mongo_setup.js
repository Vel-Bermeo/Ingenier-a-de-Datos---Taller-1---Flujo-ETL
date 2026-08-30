db = db.getSiblingDB("puffer_source");

db.createCollection("video_size");
db.createCollection("ssim");

db.video_size.createIndex({ channel: 1, video_ts: 1, format: 1 });
db.ssim.createIndex({ channel: 1, video_ts: 1, format: 1 });
