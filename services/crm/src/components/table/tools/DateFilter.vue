<script setup lang="ts">
import { ref } from "vue";

const modes = ["Промежуток"];
const currentMode = ref(0);
</script>

<template>
	<div class="date-filter">
		<div class="df-mode">
			<div class="tool-icon-wrapper">
				<div class="tool-icon calendar"></div>
			</div>
			<span class="df-title">{{ modes[currentMode] }}</span>
		</div>
		<Transition name="fade">
			<div v-if="modes[currentMode] === 'Промежуток'" class="df-input">
				<span>с</span>
				<input placeholder="01.01.2024" />
				<span>по</span>
				<input placeholder="05.01.2024" />
			</div>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.date-filter {
	@include tool;

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
				&.calendar {
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

	.df-input {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 4px;

		transform: opacity 1s;

		input {
			width: 97px;
			height: 26px;

			border: none;
			outline: none;

			padding: 4px 12px;
			border-radius: 8px;
			background-color: $fuji-white-darker;

			&::placeholder {
				font-size: 14px;
				color: $text-color;
			}
		}
	}
}
</style>
