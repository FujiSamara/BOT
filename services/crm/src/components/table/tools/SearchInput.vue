<script setup lang="ts">
import { ref } from "vue";

const props = defineProps({
	placeholder: {
		type: String,
	},
	disabled: {
		type: Boolean,
	},
	error: {
		type: String,
	},
});
const emits = defineEmits<{
	(e: "submit", value: string): void;
}>();

const active = ref(false);

let delaySetter: number = setTimeout(() => {}, 0);
const delay = 500;

const onInput = (event: Event) => {
	const val = (event.target as HTMLInputElement).value;
	clearTimeout(delaySetter);
	delaySetter = setTimeout(async () => {
		emits("submit", val);
	}, delay);
};
</script>

<template>
	<div
		class="search-input"
		:class="{ active: active, disabled: disabled, error: error !== undefined }"
	>
		<div class="si-icon-wrapper">
			<div class="si-icon search"></div>
		</div>
		<input
			@focusin="active = true"
			:disabled="disabled"
			@focusout="active = false"
			:placeholder="props.placeholder"
			@input="onInput"
		/>
		<Transition name="fade">
			<div v-show="error !== undefined" class="si-icon-wrapper">
				<div class="si-icon error"></div>
			</div>
		</Transition>

		<Transition name="fade">
			<span v-if="error !== undefined && active" class="si-message">
				{{ error }}
			</span>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.search-input {
	display: flex;
	flex-direction: row;
	align-items: center;
	position: relative;

	gap: 10px;

	padding: 15px 20px;
	border-radius: 8px;
	border: 1px solid $border-color;
	background-color: $table-bg-color;

	transition: border-color 0.25s;

	.si-icon-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 24px;
		height: 24px;

		.si-icon {
			background-color: currentColor;
			color: #090c2f99;
			width: 16px;
			height: 16px;
			fill: currentColor;

			mask-size: contain;
			mask-repeat: no-repeat;

			transition:
				color 0.25s,
				opacity 0.25s;

			&.search {
				mask-image: url("@/assets/icons/loop.svg");
			}

			&.error {
				mask-image: url("@/assets/icons/alert.svg");
				color: $danger-color;
			}
		}
	}

	input {
		display: flex;
		width: 0;
		flex-grow: 1;

		outline: none;
		border: none;

		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 14px;
		color: $text-color;
		background-color: inherit;

		&::placeholder {
			color: $text-color-lighter;

			transition: opacity 0.25s;
		}
	}

	.si-message {
		position: absolute;
		left: calc(-16px + 100%);

		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 10px;
		color: $danger-color;

		z-index: 1;
		white-space: nowrap;

		background-color: inherit;
		padding: 4px 8px;
		border-radius: 8px;
		border: 1px solid $danger-color;
	}

	&.active {
		border-color: $fuji-blue;

		.si-icon-wrapper > .si-icon {
			color: $fuji-blue;
		}

		input::placeholder {
			opacity: 0;
		}
	}

	&.disabled {
		background-color: #eeeeee;
		border-color: #cdcdcd;

		.si-icon-wrapper > .si-icon {
			color: #cdcdcd99;
		}

		input::placeholder {
			color: #cdcdcd99;
		}
	}

	&.error {
		border-color: $danger-color;

		.si-icon-wrapper > .si-icon {
			color: $danger-color;
		}

		input,
		input::placeholder {
			color: $danger-color;
		}
	}
}
</style>
