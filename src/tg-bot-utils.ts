import { minioClient } from "./minio.js";

export class TgBotUtils {
  static async pushToFmStation({
    fmStation,
    fileName,
    file,
  }: {
    fmStation: string;
    fileName: string;
    file: string;
  }) {
    await TgBotUtils.createFmStationIfNotExist({ fmStation });

    await minioClient.fPutObject(fmStation, fileName, file);
  }

  static async createFmStationIfNotExist({ fmStation }: { fmStation: string }) {
    const exists = await minioClient.bucketExists(fmStation);

    if (!exists) {
      await minioClient.makeBucket(fmStation);
    }
  }
}
