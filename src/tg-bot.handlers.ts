// import { Markup } from "telegraf";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import axios from "axios";
import { TgBotUtils } from "./tg-bot-utils.js";

export class TgBotHandlers {
  //   static async justTellUserToOpenTheWebApp(ctx: any) {

  //   }

  static async uploadAndPushSongToStorage(ctx: any, fmStation: string) {
    // TODO add users/permissions db
    console.log(
      'process.env["BOT_SUPERADMIN_ID"]',
      process.env["BOT_SUPERADMIN_ID"],
      "You",
      ctx.message.from.id
    );

    if (ctx.message.from.id !== Number(process.env["BOT_SUPERADMIN_ID"])) {
      const forbiddenMessage = `Only superadmin can upload audio files.505ATb.`;
      await ctx.telegram.sendMessage(ctx.message.chat.id, forbiddenMessage);
      return;
    }

    try {
      const { localFilePath, fileName } = await TgBotHandlers.downloadAudioFile(
        ctx
      );

      console.log("Audio file downloaded:", localFilePath);

      await TgBotUtils.pushToFmStation({
        fmStation: fmStation,
        fileName,
        file: localFilePath,
      });

      // Process the audio file as needed
      // For example, you can call TgBotUtils.extractAudio here

      // Clean up the downloaded file
      fs.unlinkSync(localFilePath);

      ctx.reply("Audio has been uploaded");
    } catch (error) {
      console.error("Error downloading audio file:", error);
    }
  }

  /**
   *
   * @param ctx Telegram context
   * @returns File path of the downloaded audio file
   */
  private static async downloadAudioFile(
    ctx: any
  ): Promise<{ localFilePath: string; fileName: string }> {
    const audio = ctx.message.audio;
    const fileId = audio.file_id;

    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);

    const downloadsDir = path.join(__dirname, "downloads");

    console.log("Checking if downloads directory exists:", downloadsDir);

    !fs.existsSync(downloadsDir) && fs.mkdirSync(downloadsDir);

    const filePath = await ctx.telegram.getFileLink(fileId);
    const fileName = path.basename(filePath.href);

    // Download the file
    const response = await axios.get(filePath.href, {
      responseType: "arraybuffer",
    });

    const arrayBuffer = response.data;

    const buffer = Buffer.from(arrayBuffer);
    const localFilePath = path.join(downloadsDir, fileName);
    fs.writeFileSync(localFilePath, buffer);

    return { localFilePath, fileName };
  }
}
