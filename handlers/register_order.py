# builder = ReplyKeyboardBuilder()
# if client.vehicleList is not None:
#     for vehicle in client.vehicleList:
#         builder.row(
#             KeyboardButton(text=utils.build_vehicle_name(vehicle))
#         )
# builder.row(KeyboardButton(text="🚗 Регистрация нового ТС"))
# builder.row(KeyboardButton(text="↩️ В начало"))
# await message.answer("Вы",
#                      parse_mode="HTML",
#                      reply_markup=builder.as_markup(resize_keyboard=True))
