<script setup lang="ts">
import { ref, useId } from "vue";

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
	value: {
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
		<div class="tool-icon-wrapper">
			<div class="tool-icon search"></div>
		</div>
		<input
			@focusin="active = true"
			:disabled="disabled"
			@focusout="active = false"
			:placeholder="props.placeholder"
			@input="onInput"
			:value="value"
			:id="useId()"
		/>
		<Transition name="fade">
			<div v-show="error !== undefined" class="tool-icon-wrapper">
				<div class="tool-icon error"></div>
			</div>
		</Transition>

		<Transition name="fade">
			<span
				v-if="error !== undefined && active && error !== ''"
				class="tool-message"
			>
				{{ error }}
			</span>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.search-input {
	@include field;

	.tool-icon-wrapper {
		.tool-icon {
			width: 16px;
			height: 16px;

			&.search {
				mask-image: url("@/assets/icons/loop.svg");
				color: #090c2f99;
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

		box-shadow: 0 0 0px 1000px white inset !important;

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

	&.active {
		input::placeholder {
			opacity: 0;
		}
	}

	&:hover,
	&.active {
		.tool-icon-wrapper {
			.tool-icon {
				&.search {
					color: $fuji-blue;
				}
			}
		}
	}

	&.disabled {
		input::placeholder {
			color: #cdcdcd99;
		}
	}

	&.error {
		input,
		input::placeholder {
			color: $danger-color;
		}
	}
}
</style>
