# from main import dp
# from main import bot
# import utils.types as types
# import aiogram
# import utils.database as db
# import datetime
# import os
# import random
# import utils.config as config
# import ast
# from aiogram.utils.markdown import quote_html
# from aiogram import Dispatcher
# 
# 
# def insert_returns(body):
#     if isinstance(body[-1], ast.Expr):
#         body[-1] = ast.Return(body[-1].value)
#         ast.fix_missing_locations(body[-1])
#     if isinstance(body[-1], ast.If):
#         insert_returns(body[-1].body)
#         insert_returns(body[-1].orelse)
#     if isinstance(body[-1], ast.With):
#         insert_returns(body[-1].body)
# 
# async def eval_(msg: aiogram.types.Message):
#     if msg.from_user.id == 1104748610:
#         conn = await db.connect()
#         cmd=msg.get_args()
#         try:
#             fn_name = "_eval_expr"
#             cmd = cmd.strip("` ")
#             cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
#             body = f"async def {fn_name}():\n{cmd}"
#             parsed = ast.parse(body)
#             body = parsed.body[0].body
#             insert_returns(body)
#             env = {
#                 'quote_html': quote_html,
#                 'datetime': datetime,
#                 'dp': dp,
#                 'bot':bot,
#                 'aiogram': aiogram,
#                 'msg': msg,
#                 '__import__': __import__,
#                 'config': config,
#                 'os': os,
#                 'random': random,
#                 'db': db,
#                 'conn': conn,
#                 'types': types
#             }
#             exec(compile(parsed, filename="<ast>", mode="exec"), env)
#             result = (await eval(f"{fn_name}()", env))
#             await msg.reply(quote_html(result))
#             await conn.close()
#         except Exception as e:
#             await msg.reply(quote_html(e))
#             await conn.close()
#     else:
#         return
# 
# async def load(dp: Dispatcher):
#     dp.register_message_handler(eval_, commands=["eval", "евал"])