<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

const props = defineProps({
	title: {
		type: String,
	},
	height: {
		type: String,
	},
});
const emits = defineEmits(["close"]);

const keyDown = (e: KeyboardEvent) => {
	if (e.key === "Escape") {
		emits("close");
	}
};

onMounted(() => {
	document.addEventListener("keydown", keyDown);
});

onUnmounted(() => {
	document.removeEventListener("keydown", keyDown);
});
</script>

<template>
	<div class="bm-wrapper" @mousedown="emits('close')">
		<div class="bm-window" @mousedown.stop :style="{ height: props.height }">
			<div class="bm-title">
				<!--stub-->
				<div></div>
				<span>{{ props.title }}</span>
				<div class="icon-wrapper" @click="emits('close')">
					<div class="icon cross"></div>
				</div>
			</div>
			<slot></slot>
		</div>
	</div>
</template>

<style scoped lang="scss">
.bm-wrapper {
	display: flex;
	justify-content: center;
	align-items: center;

	left: 0;
	top: 0;
	position: fixed;

	z-index: 2;
	width: 100%;
	height: 100%;

	background: rgba(255, 255, 255, 0.1);
	backdrop-filter: blur(22px);

	.bm-window {
		display: flex;
		flex-direction: column;

		overflow-y: auto;

		gap: 24px;
		padding: 16px;
		border-radius: 16px;
		width: 640px;
		min-height: 100px;
		max-height: 90%;

		background: $main-white;
		box-shadow: 0px 6px 16px 0px rgba(0, 0, 0, 0.1);

		.bm-title {
			display: flex;
			flex-direction: row;
			justify-content: space-between;

			padding: 8px 16px;

			color: $main-dark-gray;
			font-family: Wix Madefor Display;
			font-size: 16px;
			font-weight: 500;
			line-height: 20.16px;

			.icon-wrapper {
				display: flex;
				justify-content: center;
				align-items: center;
				width: 24px;
				height: 24px;
				cursor: pointer;

				.icon {
					width: 12px;
					height: 12px;
					background-color: currentColor;
					fill: currentColor;

					transition:
						color 0.25s,
						transform 0.25s;

					&.cross {
						mask: url("@/assets/icons/cross.svg") no-repeat;
					}
				}

				&:hover {
					color: $main-accent-blue;

					.icon {
						transform: rotate(90deg);
					}
				}
			}
		}
	}
}
</style>
