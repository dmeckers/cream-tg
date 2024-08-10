import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import "dotenv/config";
import { Markup, Telegraf } from "telegraf";
import { message } from "telegraf/filters";
import { TgBotHandlers } from "./tg-bot.handlers.js";
// import { ReplyKeyboard } from "node-telegram-keyboard-wrapper";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_MASTER_PATH = path.join(
  __dirname,
  "../../channels/master/playlists/master"
);

const app = express();
const token = process.env["BOT_TOKEN"] || "too sad for you :(";
const stations = ["cream"];
const userStations = new Map<string, string>();
const bot = new Telegraf(token);

const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("audio"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  const targetPath = path.join(TEST_MASTER_PATH, req.file.originalname);

  return fs.rename(req.file.path, targetPath, (err) =>
    err
      ? res
          .status(500)
          .send(`Error saving file. - ${err.message}. \n Stack: ${err.stack}`)
      : res.send("File uploaded successfully.")
  );
});

bot.command("help", (ctx) => {
  ctx.reply(
    "Commands: \n /stations - list of stations \n /currentStation - current station"
  );
});

bot.command("stations", (ctx) => {
  const stationButtons = stations.map((station) =>
    Markup.button.callback(station, `choose_station_${station}`)
  );
  ctx.reply(
    "Choose a station:",
    Markup.inlineKeyboard(
      [
        ...stationButtons,
        Markup.button.callback("Create station", `create_station`),
      ],
      { columns: 1 }
    )
  );
});

bot.command("currentStation", (ctx) => {
  const station = userStations.get(ctx.from.id.toString());
  ctx.reply(`Your current station is ${station}`);
});

// Handle station selection
bot.action(/choose_station_(.+)/, (ctx) => {
  const station = ctx.match[1];
  userStations.set(ctx.from.id.toString(), station!);
  ctx.reply(`You have selected ${station}`);
});

// Handle station selection
bot.action(/create_station/, (ctx) => {
  ctx.reply("Enter the name of the station you want to create inside of <>:");
});

/**
 * Just drains all text messages and sends a hardcoded message back.
 */
bot.on(message("text"), async (ctx) => {
  const messageText = ctx.message.text;
  const matchAdd = messageText.match(/^<(.+)>$/);
  const matchRemove = messageText.match(/^>(.+)<$/);

  if (matchAdd) {
    const stationName = matchAdd[1];
    stations.push(stationName!);
    ctx.reply(`Station ${stationName} has been created.`);
    return;
  }

  if (matchRemove) {
    const stationName = matchRemove[1];
    const index = stations.indexOf(stationName!);
    if (index > -1) {
      stations.splice(index, 1);
      ctx.reply(`Station ${stationName} has been removed.`);
    } else {
      ctx.reply(`Station ${stationName} does not exist.`);
    }
    return;
  }

  await ctx.telegram.sendMessage(
    ctx.message.chat.id,
    `Wassup ma nigga, hope u doin good. I'm just a fucking piece of hardcoded message. Hit button bellow to open radio.`
  );

  await ctx.reply(
    "Welcome",
    Markup.keyboard([
      Markup.button.webApp(
        "Open Web App",
        process.env["WEB_APP_URL"] ||
          "https://dmeckers.github.io/cream-fm-bot-app/"
      ),
    ])
  );
});

bot.on(message("audio"), async (ctx) => {
  await TgBotHandlers.uploadAndPushSongToStorage(
    ctx,
    `${userStations.get(`${ctx.from.id}`) || "cream"}`
  );
});

bot.launch();

app.listen(3003, () => {
  console.log("Server is running on port 3003");
});
