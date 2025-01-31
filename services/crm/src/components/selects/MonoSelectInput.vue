<script setup lang="ts">
import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import { computed, PropType, ref } from "vue";
import * as animations from "@/components/selects/monoSelectAnimations";

const props = defineProps({
	error: {
		type: String,
	},
	placeholder: {
		type: String,
	},
	searchList: {
		type: Array as PropType<string[]>,
		required: true,
	},
	searchValue: {
		type: String,
		required: true,
	},
	required: {
		type: Boolean,
		default: false,
	},
});
const emits = defineEmits<{
	(e: "select", index: number): void;
	(e: "submit", value: string): void;
	(e: "close"): void;
}>();

const active = ref(false);

const list = computed(() => {
	if (!active.value) {
		return [];
	}
	return props.searchList;
});

const focusOut = () => {
	active.value = false;

	emits("close");
};
</script>

<template>
	<div class="msi-wrapper" @focusin="active = true" @focusout="focusOut">
		<MaybeDelayInput
			class="msi-input"
			:value="searchValue"
			@submit="(val: string) => emits('submit', val)"
			:error="props.error"
			:placeholder="props.placeholder"
			:with-search-icon="false"
			:with-edit-mark="true"
			:required="props.required"
		></MaybeDelayInput>
		<Transition name="fade">
			<div class="msi-list-wrapepr" v-show="list.length">
				<TransitionGroup
					:css="false"
					tag="ul"
					class="msi-list"
					@before-enter="animations.onBeforeEnter"
					@enter="animations.onEnter"
					@leave="animations.onLeave"
					@pointerdown.prevent
				>
					<li
						class="msi-row"
						:key="row"
						v-for="(row, index) in list"
						:data-index="index"
						@click="emits('select', index)"
					>
						<span>
							{{ row }}
						</span>
					</li>
				</TransitionGroup>
			</div>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.msi-wrapper {
	display: flex;
	flex-direction: column;
	position: relative;

	.msi-input {
		width: 100%;
		height: 48px;
	}

	.msi-list-wrapepr {
		position: absolute;
		top: 48px;
		left: 0;
		width: 100%;

		border-radius: 8px;
		border: 1px solid $stroke-gray;
		background-color: $main-white;
		padding: 16px;

		.msi-list {
			display: flex;
			flex-direction: column;

			width: 100%;
			margin: 0;
			padding: 0;
			max-height: 86px;
			overflow-y: scroll;

			.msi-row {
				display: flex;
				align-items: center;

				padding: 8px;
				margin-top: 4px;
				height: fit-content;
				width: 100%;

				span {
					font-family: Wix Madefor Display;
					font-size: 14px;
					font-weight: 500;
					line-height: 17.64px;
				}

				&:hover {
					cursor: pointer;
					background-color: $bg-light-blue;
				}

				&:first-child {
					margin-top: 0 !important;
				}

				transition: background-color 0.25s;
			}

			transition: margin-top 0.25s;
		}
	}
}
</style>
