<script setup lang="ts">
import { onMounted, onUnmounted, PropType, ref } from "vue";
import { CalendarType, DateType } from "@/types";
import DateCalendar from "@/components/DateCalendar.vue";

const props = defineProps({
	mode: {
		type: String as PropType<DateType>,
		default: DateType.Month,
	},
});

const calendarVisible = ref(true);

const from = ref(new Date());
const to = ref(new Date());

const monthChanged = (date: Date) => {
	calendarVisible.value = false;
	setIntervalFromDay(date);
};
// TODO: Complete for day and year

const setIntervalFromDay = (date: Date) => {
	from.value = new Date(date.getFullYear(), date.getMonth(), 1, 0, 0, 0, 0);
	to.value = new Date(date.getFullYear(), date.getMonth() + 1, 1, 0, 0, 0, 0);
};

const calendarOutsideClicked = () => {
	calendarVisible.value = false;
};

onMounted(() => {
	setIntervalFromDay(new Date());

	document.addEventListener("click", calendarOutsideClicked);
});

onUnmounted(() => {
	document.removeEventListener("click", calendarOutsideClicked);
});
</script>

<template>
	<div class="date-filter">
		<div class="df-mode">
			<div class="tool-icon-wrapper">
				<div class="tool-icon calendar-icon"></div>
			</div>
			<span class="df-title">{{ props.mode.toString() }}</span>
		</div>

		<!-- Modes -->
		<Transition name="fade">
			<div v-if="props.mode === DateType.Interval" class="df-value">
				<span>с</span>
				<input placeholder="01.01.2024" />
				<span>по</span>
				<input placeholder="05.01.2024" />
			</div>
		</Transition>
		<Transition name="fade">
			<div v-if="props.mode === DateType.Month" class="df-value">
				<span @click.stop="calendarVisible = !calendarVisible">{{
					from.toLocaleString("ru", { month: "long" })
				}}</span>
			</div>
		</Transition>

		<Transition name="fade">
			<DateCalendar
				v-if="calendarVisible"
				class="calendar"
				:lock-mode="CalendarType.Month"
				:date="from"
				@submit="monthChanged"
				@click.stop
			></DateCalendar>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.date-filter {
	@include field;

	width: fit-content !important;

	gap: 8px;

	.df-mode {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 8px;

		padding: 4px 16px;
		background-color: $fuji-gray;
		border-radius: 8px;

		.tool-icon-wrapper {
			width: 16px;
			height: 16px;

			.tool-icon {
				&.calendar-icon {
					width: 16px;
					height: 16px;
					color: $fuji-white;
					mask-image: url("@/assets/icons/calendar.svg");
				}
			}
		}

		.df-title {
			color: $fuji-white;
			font-size: 14px;
		}
	}

	.df-value {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 4px;

		transform: opacity 1s;
		cursor: pointer;

		span {
			display: flex;
			justify-content: center;
			align-items: center;
			width: 97px;
			height: 26px;

			padding: 4px 12px;
			border-radius: 8px;
			background-color: $fuji-white-darker;

			font-family: Wix Madefor Display;
			font-weight: 500;
			font-size: 14px;
			color: $text-color;

			text-transform: capitalize;
		}
	}

	.calendar {
		position: absolute;

		top: 100%;
		left: 0;
	}

	&:hover {
		border-color: $border-color;
	}
}
</style>
