import { Client as MinioClient } from "minio";

const minioConfig = {
  endPoint: process.env["MINIO_HOST"] || "minio-dev",
  port: 9000,
  useSSL: false,
  accessKey: process.env["MINIO_ACCESS_KEY"] || "minio",
  secretKey: process.env["MINIO_SECRET_KEY"] || "minio123",
};

export const minioClient = new MinioClient(minioConfig);
