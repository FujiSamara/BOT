<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { CalendarType } from "@/types";
import { capitalize } from "@/parser";

const props = defineProps({
	lockMode: {
		type: Number as PropType<CalendarType>,
	},
	date: {
		type: Date,
	},
	blockUnset: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "submit", value: Date): void;
	(e: "unset"): void;
}>();

const year = ref(props.date?.getFullYear() || new Date().getFullYear());
const month = ref(props.date?.getMonth());
const day = ref(props.date?.getDate());
const getDate = () => {
	const date = new Date();

	date.setFullYear(year.value);

	if (month.value !== undefined) {
		date.setMonth(month.value);
	}

	if (day.value !== undefined) {
		date.setDate(day.value);
	}

	return date;
};

const step = ref(
	props.lockMode !== undefined ? props.lockMode : CalendarType.Month,
);
const previosStep = () => {
	switch (step.value) {
		case CalendarType.Month:
			return;
		case CalendarType.Day:
			month.value = undefined;
			step.value = CalendarType.Month;
	}
};
const arrowClicked = (value: number) => {
	switch (step.value) {
		case CalendarType.Month:
			year.value += value;
			return;
		case CalendarType.Day:
			month.value = new Date(2000, month.value! + value, 1).getMonth();
	}
};

const header = computed(() => {
	const date = getDate();
	switch (step.value) {
		case CalendarType.Month:
			return date.getFullYear().toString();
		case CalendarType.Day:
			return date.toLocaleString("ru", { month: "long" });
	}
});

// Constant methods
const getMonths = (): number[][] => {
	const result = [];

	for (let i = 0; i < 4; i++) {
		const line = [];
		for (let j = 0; j < 3; j++) {
			const index = i * 3 + j;

			line.push(index);
		}
		result.push(line);
	}
	return result;
};
const getDays = (): number[][] => {
	const maxDay = new Date(year.value, month.value! + 1, 0).getDate();

	const result = [];

	for (let i = 0; i < 5; i++) {
		const line = [];
		for (let j = 0; j < 7; j++) {
			const index = i * 7 + j + 1;

			if (index > maxDay) {
				break;
			}

			line.push(index);
		}
		result.push(line);
	}
	return result;
};
//

const toMonth = (month: number): string => {
	return new Date(year.value, month).toLocaleString("ru", {
		month: "long",
	});
};

const monthChoosed = (currentMonth: number) => {
	month.value = currentMonth;
	if (props.lockMode === undefined || props.lockMode !== CalendarType.Month) {
		step.value = CalendarType.Day;
		return;
	}

	if (props.date && currentMonth === month.value) {
		if (props.blockUnset) return;
		month.value = undefined;
		emits("unset");
		return;
	}

	if (props.lockMode) emits("submit", getDate());
};
const dayChoosed = (currentDay: number) => {
	day.value = currentDay;

	if (props.date && currentDay === day.value) {
		if (props.blockUnset) return;
		day.value = undefined;
		emits("unset");
		return;
	}

	emits("submit", getDate());
};
</script>
<template>
	<div class="calendar">
		<div class="c-header">
			<div class="switch" @click="() => arrowClicked(-1)">
				<span class="arrow"></span>
			</div>
			<span class="header" @click="previosStep">{{ capitalize(header) }}</span>
			<div class="switch" @click="() => arrowClicked(1)">
				<span class="arrow reversed"></span>
			</div>
		</div>
		<Transition name="fade" mode="out-in">
			<div v-if="step === CalendarType.Month" class="months c-body">
				<div class="c-line" v-for="line in getMonths()">
					<div
						@click="monthChoosed(lineMonth)"
						class="c-element"
						v-for="lineMonth in line"
						:class="{ choosed: month === lineMonth }"
					>
						<span>{{ capitalize(toMonth(lineMonth)) }}</span>
					</div>
				</div>
			</div>

			<div v-else-if="step === CalendarType.Day" class="days c-body">
				<div class="c-line" v-for="line in getDays()">
					<div
						@click="dayChoosed(lineDay)"
						class="c-element"
						v-for="lineDay in line"
						:class="{ choosed: day && day === lineDay }"
					>
						<span>{{ lineDay }}</span>
					</div>
				</div>
			</div>
		</Transition>
	</div>
</template>
<style lang="scss" scoped>
.calendar {
	@include window();

	z-index: 1;

	flex-direction: column;
	align-items: center;

	width: 284px;
	height: fit-content;
	padding: 16px;
	gap: 16px;

	font-family: Wix Madefor Display;
	font-weight: 500;
	font-size: 14px;
	color: $main-dark-gray;

	.c-header {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;

		width: 100%;
		height: 24px;

		.header {
			font-size: 14px;
			cursor: pointer;
		}

		.switch {
			display: flex;
			justify-content: center;
			align-items: center;

			width: 24px;
			height: 24px;
			border-radius: 8px;
			border: 1px solid $stroke-light-blue;
			cursor: pointer;

			transform: rotate(90deg);

			.arrow {
				@include arrow();
				color: $main-dark-gray;
			}

			&:hover {
				border-color: $main-accent-blue;
			}

			transition: border-color 0.25s;
		}
	}

	.c-body {
		display: flex;
		flex-direction: column;
		gap: 8px;

		.c-line {
			display: flex;
			flex-direction: row;
			gap: 8px;

			.c-element {
				display: flex;
				align-items: center;
				justify-content: center;

				min-width: 72px;
				height: 24px;
				padding: 3px 8px;
				border-radius: 4px;
				cursor: pointer;

				text-align: center;
				font-size: 12px;

				transition:
					background-color 0.25s,
					color 0.25s;

				&:hover,
				&.choosed {
					background-color: $main-dark-gray;
					color: $main-white;
				}
			}
		}

		&.days {
			.c-element {
				width: 24px;
				min-width: 0;
			}
		}
	}
}
</style>
