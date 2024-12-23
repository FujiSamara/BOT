<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { CalendarType } from "@/types";

const props = defineProps({
	lockMode: {
		type: Number as PropType<CalendarType>,
	},
	date: {
		type: Date,
	},
});
const emits = defineEmits<{
	(e: "submit", value: Date): void;
}>();

const step = ref(
	props.lockMode !== undefined ? props.lockMode : CalendarType.Month,
);

const date = ref(props.date ? props.date : new Date());

const header = computed(() => {
	switch (step.value) {
		case CalendarType.Year:
			return date.value.getFullYear();
		default:
			return date.value.toLocaleString("ru", { month: "long" });
	}
});

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

const monthChoosed = (month: number) => {
	const temp = new Date(date.value);
	temp.setMonth(month);
	date.value = temp;
	if (props.lockMode) {
		emits("submit", date.value);
	}
	step.value = CalendarType.Day;
};
</script>
<template>
	<div class="calendar">
		<div class="c-header">
			<div class="switch">
				<span class="arrow"></span>
			</div>
			<span class="header">{{ header }}</span>
			<div class="switch">
				<span class="arrow reversed"></span>
			</div>
		</div>
		<Transition name="fade">
			<div v-if="step === CalendarType.Month" class="months c-body">
				<div class="c-line" v-for="line in getMonths()">
					<div
						@click="if (month !== date.getMonth()) monthChoosed(month);"
						class="c-element"
						v-for="month in line"
						:class="{ choosed: month === date.getMonth() }"
					>
						<span>{{
							new Date(date.getFullYear(), month).toLocaleString("ru", {
								month: "long",
							})
						}}</span>
					</div>
				</div>
			</div>
		</Transition>
		<Transition name="fade"></Transition>
		<!-- TODO: Complete calendar for day and year -->
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

	text-transform: capitalize;
	font-family: Wix Madefor Display;
	font-weight: 500;
	font-size: 14px;
	color: $text-color;

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
			border: 1px solid $fuji-blue-lightest;
			cursor: pointer;

			transform: rotate(90deg);

			.arrow {
				@include arrow();
				color: $text-color;
			}

			&:hover {
				border-color: $fuji-blue;
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
					background-color: $text-color;
					color: $fuji-white;
				}
			}
		}
	}
}
</style>
