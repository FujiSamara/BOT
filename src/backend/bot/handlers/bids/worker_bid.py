from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
import bot.kb as kb
from bot.handlers import utils
from bot.states import WorkerBidCreating, Base
from db import service


router = Router(name="worker_bid")


@router.callback_query(F.data == "get_worker_bid_menu")
async def get_worker_bid_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=callback.message,
        text=hbold("Согласование кандидатов"),
        reply_markup=kb.worker_bid_menu,
    )


async def send_create_worker_bid_menu(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    await utils.try_edit_or_answer(
        message=message,
        text=hbold("Согласование кандидатов"),
        reply_markup=await kb.get_create_worker_bid_menu(state),
    )


@router.callback_query(F.data == "get_create_worker_bid_menu")
async def get_create_worker_bid_menu(callback: CallbackQuery, state: FSMContext):
    await send_create_worker_bid_menu(callback.message, state)


# First name
@router.callback_query(F.data == "get_worker_bid_fname_form")
async def get_worker_bid_fname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.f_name)
    await utils.try_edit_message(message=callback.message, text=hbold("Введите имя:"))


@router.message(WorkerBidCreating.f_name)
async def set_worker_bid_fname(message: Message, state: FSMContext):
    await state.update_data(f_name=message.text)
    await send_create_worker_bid_menu(message, state)


# Last name
@router.callback_query(F.data == "get_worker_bid_lname_form")
async def get_worker_bid_lname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.l_name)
    await utils.try_edit_message(
        message=callback.message, text=hbold("Введите фамилию:")
    )


@router.message(WorkerBidCreating.l_name)
async def set_worker_bid_lname(message: Message, state: FSMContext):
    await state.update_data(l_name=message.text)
    await send_create_worker_bid_menu(message, state)


# Patronymic
@router.callback_query(F.data == "get_worker_bid_oname_form")
async def get_worker_bid_oname_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.o_name)
    await utils.try_edit_message(
        message=callback.message, text=hbold("Введите отчество:")
    )


@router.message(WorkerBidCreating.o_name)
async def set_worker_bid_oname(message: Message, state: FSMContext):
    await state.update_data(o_name=message.text)
    await send_create_worker_bid_menu(message, state)


# Post
@router.callback_query(F.data == "get_worker_bid_post_form")
async def get_worker_bid_post_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkerBidCreating.post)
    posts = service.get_posts()
    await utils.try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите должность:"),
        reply_markup=kb.create_reply_keyboard(*[post.name for post in posts]),
    )
    await state.update_data(msg=msg)


@router.message(WorkerBidCreating.post)
async def set_worker_bid_post(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await utils.try_delete_message(msg)
    await state.update_data(post=message.text)
    await utils.try_delete_message(message)
    await send_create_worker_bid_menu(message, state)
