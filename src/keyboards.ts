// import {
//   KeyboardButton,
//   ReplyKeyboard,
//   Row,
// } from "node-telegram-keyboard-wrapper";

// export const manageKeyboard = ({
//   selectedFmStation,
// }: {
//   selectedFmStation: string | undefined;
// }) =>
//   selectedFmStation
//     ? new ReplyKeyboard(
//         new Row(
//           new KeyboardButton("Create Station"),
//           new KeyboardButton("Select Station")
//         ),
//         new Row(
//           new KeyboardButton("Delete Station"),
//           new KeyboardButton("List Tracks")
//         ),
//         new Row(
//           new KeyboardButton("Push Jiggle"),
//           new KeyboardButton("Delete Track")
//         ),
//         new Row(new KeyboardButton("Mix Up"), new KeyboardButton("Stream?"))
//       )
//     : new ReplyKeyboard(new Row(new KeyboardButton("Create Station")));
