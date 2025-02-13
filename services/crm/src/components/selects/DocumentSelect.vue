<script setup lang="ts">
import { computed, PropType, useTemplateRef } from "vue";
import { DocumentSchema } from "@/types";
import { fileToDocumentSchema } from "@/parser";
import DefaultButton from "../UI-new/DefaultButton.vue";

const props = defineProps({
	documents: {
		type: Array as PropType<DocumentSchema[]>,
		required: true,
	},
	onlyOne: {
		type: Boolean,
	},
	placeholder: {
		type: String,
	},
	readonly: {
		type: Boolean,
	},
	required: {
		type: Boolean,
	},
	error: {
		type: String,
	},
	errorLeftAlign: {
		type: Boolean,
		default: false,
	},
});
const emits = defineEmits<{
	(e: "submit", documents: DocumentSchema[]): void;
	(e: "clear"): void;
}>();

const inputRef = useTemplateRef("input");

const showAdd = computed(() => {
	return (!props.onlyOne || props.documents.length === 0) && !props.readonly;
});
const createTitle = computed(
	() => "Добавить файл" + (props.onlyOne ? "" : "ы"),
);

const addFile = async (event: Event) => {
	const target = event.target as HTMLInputElement;
	const files = target.files!;
	const documents = [];

	for (const file of files) {
		documents.push(await fileToDocumentSchema(file));
	}
	emits("submit", documents);
};
</script>

<template>
	<div class="ds-wrapper" :class="{ error: error !== undefined }">
		<input
			type="file"
			:multiple="!props.onlyOne"
			ref="input"
			@change.prevent="addFile"
		/>
		<!-- Hint + Docs + Delete -->
		<div class="ds-outer">
			<!-- Hint -->
			<Transition name="fade" mode="out-in">
				<div
					class="ds-inner"
					v-if="props.placeholder && !props.documents.length"
				>
					<span class="hint">{{ props.placeholder }} </span>
					<span class="required" v-if="props.required && !props.readonly">
						<span class="stub">{{ props.placeholder }}</span>
						<span>*</span>
					</span>
				</div>
				<!-- Docs + Delete -->
				<div class="ds-inner" v-else-if="props.documents.length">
					<ul class="documents">
						<li class="document" v-for="document in props.documents">
							{{ document.name }}
						</li>
					</ul>
					<DefaultButton
						class="delete"
						title=""
						v-if="!props.readonly"
						@click="emits('clear')"
					>
						<div class="tool-icon-wrapper">
							<div class="tool-icon bin"></div>
						</div>
					</DefaultButton>
				</div>
			</Transition>
		</div>

		<!-- Add + Error -->
		<Transition name="fade" mode="out-in">
			<DefaultButton
				v-if="showAdd && error === undefined"
				class="add"
				title=""
				@click="() => inputRef?.click()"
			>
				<div class="tool-icon-wrapper"><div class="tool-icon plus"></div></div>
				<span>{{ createTitle }}</span>
			</DefaultButton>
			<div class="error-wrapper" v-else-if="error !== undefined">
				<Transition name="fade">
					<span
						v-if="error"
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
.ds-wrapper {
	@include field;

	flex-grow: 1;

	width: unset;
	height: 48px;

	.ds-outer {
		display: flex;
		flex-direction: row;
		align-items: center;

		flex-grow: 1;
		flex-basis: 0;

		height: 32px;

		.ds-inner {
			display: flex;
			flex-direction: row;
			align-items: center;
			gap: 10px;

			height: 100%;
			width: 0;
			min-width: 0;
			flex-grow: 1;

			.hint {
				background-color: transparent;
				color: $sec-dark-gray-25;
			}

			.required {
				user-select: none;

				span {
					color: $sec-arrantion-red;
					font-family: Wix Madefor Display;
					font-size: 12px;
					font-weight: 500;

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

			::-webkit-scrollbar {
				display: none;
			}

			.documents {
				display: flex;
				flex-direction: row;
				gap: 10px;

				height: 100%;
				width: fit-content;
				min-width: 0;
				flex-grow: 0;

				padding: 0;
				margin: 0;

				overflow-x: scroll;
				-ms-overflow-style: none; /* IE и Edge */
				scrollbar-width: none; /* Firefox */
				list-style: none;

				.document {
					margin: 0;
					padding: 8px 14px;

					max-width: 110px;
					min-width: 110px;
					width: 110px;
					max-height: 100%;

					color: $main-accent-blue !important;
					font-family: Wix Madefor Display;
					font-size: 12px;
					font-weight: 500;

					border-radius: 4px;
					background-color: $bg-light-blue;

					white-space: nowrap;

					text-overflow: ellipsis;
					overflow: hidden;
				}
			}

			.delete {
				min-width: 110px;
				max-width: 110px;
				width: 110px;
				height: 100%;

				flex-grow: 1;

				background-color: $sec-arrantion-red;

				.tool-icon-wrapper {
					height: 16px;
					width: 16px;
					.tool-icon {
						color: $main-white;
						width: 9px;
						height: 10px;

						&.bin {
							mask-image: url("@/assets/icons/bin.svg");
						}
					}
				}
			}
		}
	}

	button.add {
		margin-left: auto;

		gap: 10px;

		width: 144px;
		height: 32px;

		background-color: $main-accent-blue;
		transition: background-color 0.25s;

		span {
			font-family: Wix Madefor Display;
			font-weight: 500;
			font-size: 12px;
			color: $main-white;

			transition: color 0.25s;
		}

		.tool-icon-wrapper {
			height: 16px;
			width: 16px;
			.tool-icon {
				color: $main-white;
				width: 8px;
				height: 8px;

				&.plus {
					mask-image: url("@/assets/icons/plus.svg");
				}
			}
		}

		&:not(.readonly) {
			&:hover {
				.tool-icon-wrapper .tool-icon,
				span {
					color: $main-accent-blue;
				}
				background-color: $main-white;
			}
		}
	}

	.error-wrapper {
		position: relative;
		display: flex;
		flex-direction: row;

		background-color: inherit;
		z-index: 1;

		.tool-icon-wrapper {
			.tool-icon {
				width: 16px;
				height: 16px;
				&.error {
					mask-image: url("@/assets/icons/alert.svg");
					color: $sec-arrantion-red;
				}
			}
		}

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

	input[type="file"] {
		width: 0;
		overflow: hidden;
		opacity: 0;
		display: inline;
		position: absolute;
	}

	&:not(.readonly) {
		&:hover .tool-icon-wrapper .tool-icon {
			color: $main-white;
		}
	}

	&.error {
		button.add {
			.tool-icon-wrapper .tool-icon,
			span {
				color: $main-white !important;
			}
		}
	}
}
</style>
