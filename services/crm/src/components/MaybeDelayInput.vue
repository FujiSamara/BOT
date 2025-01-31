<script setup lang="ts">
import { computed, Ref, ref, useId, useTemplateRef } from "vue";

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
	errorLeftAlign: {
		type: Boolean,
		default: false,
	},
	value: {
		type: String,
	},
	withSearchIcon: {
		type: Boolean,
		default: true,
	},
	withEditMark: {
		type: Boolean,
		default: false,
	},
	required: {
		type: Boolean,
		default: false,
	},
});
const emits = defineEmits<{
	(e: "submit", value: string): void;
}>();

const active = ref(false);
const input = useTemplateRef("input");
const tempValue: Ref<string | undefined> = ref(undefined);
const value = computed(() => {
	if (tempValue.value === undefined) {
		return props.value;
	}
	return tempValue.value;
});

let delaySetter: number = setTimeout(() => {}, 0);
const delay = 500;

const onInput = (event: Event) => {
	const val = (event.target as HTMLInputElement).value;
	tempValue.value = val;
	clearTimeout(delaySetter);
	delaySetter = setTimeout(async () => {
		tempValue.value = undefined;
		emits("submit", val);
	}, delay);
};
const starClicked = () => {
	input.value!.focus();
};
</script>

<template>
	<div
		class="search-input"
		:class="{ active: active, disabled: disabled, error: error !== undefined }"
	>
		<div class="tool-icon-wrapper" v-if="props.withSearchIcon">
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
			ref="input"
		/>
		<Transition name="fade">
			<span
				class="required"
				v-if="!active && props.required && !value"
				@click="starClicked"
			>
				<span class="stub">{{ props.placeholder }}</span>
				<span>*</span>
			</span>
		</Transition>
		<Transition name="fade">
			<div
				v-if="props.withEditMark && error === undefined"
				class="tool-icon-wrapper edit"
			>
				<div class="tool-icon edit"></div>
			</div>
		</Transition>

		<Transition name="fade">
			<div class="error-wrapper" v-show="error !== undefined">
				<Transition name="fade">
					<span
						v-if="active && error"
						class="tool-message"
						:class="{ left: props.errorLeftAlign }"
					>
						{{ error }}
					</span>
				</Transition>
				<div class="tool-icon-wrapper">
					<div class="tool-icon error"></div>
				</div>
			</div>
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
				color: $main-dark-gray;
			}

			&.error {
				mask-image: url("@/assets/icons/alert.svg");
				color: $sec-arrantion-red;
			}

			&.edit {
				mask-image: url("@/assets/icons/pencil.svg");
				color: $main-dark-gray;
			}
		}

		&.edit.fade-enter-active,
		&.edit.fade-leave-active {
			position: absolute;
			right: 20px;
		}
	}

	input {
		display: flex;
		width: 0;
		flex-grow: 1;
		padding: 0;

		outline: none;
		border: none;

		box-shadow: 0 0 0px 1000px white inset !important;

		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 14px;
		color: $main-dark-gray;
		background-color: inherit;

		&::placeholder {
			color: $sec-dark-gray-25;

			transition: opacity 0.25s;
		}
	}

	.error-wrapper {
		position: relative;
		display: flex;
		flex-direction: row;

		background-color: inherit;
		z-index: 1;

		.tool-message {
			left: 100%;
			top: 0;

			&.left {
				position: relative;
				left: unset;
				top: unset;
			}
		}
	}

	.required {
		span {
			color: $sec-arrantion-red;
			font-family: Wix Madefor Display;
			font-size: 12px;
			font-weight: 500;
			line-height: 15.12px;

			vertical-align: text-top;
		}

		.stub {
			opacity: 0;
			font-size: 14px;
		}

		position: absolute;
		top: 12px;
		left: 25px;

		&.fade-enter-active,
		&.fade-leave-active {
			transition: opacity 0.25s !important;
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
					color: $main-accent-blue;
				}

				&.edit {
					color: $main-white;
				}
			}

			&.edit {
				background-color: $main-accent-blue;
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
			color: $sec-arrantion-red;
		}
	}
}
</style>
