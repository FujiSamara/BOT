<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

const props = defineProps({
	style: {
		type: String,
	},
	alignRight: {
		type: Boolean,
	},
});

const menuVisible = ref(false);
const menuOutsideClicked = () => {
	menuVisible.value = false;
};

onMounted(() => {
	document.addEventListener("click", menuOutsideClicked);
});
onUnmounted(() => {
	document.removeEventListener("click", menuOutsideClicked);
});
</script>

<template>
	<div class="drop-down">
		<button
			@click.stop="menuVisible = !menuVisible"
			:class="{ active: menuVisible }"
			:style="props.style"
			class="dd-switch"
		>
			<slot name="title"></slot>
		</button>
		<Transition name="fade">
			<ul
				class="dd-menu"
				@click.stop
				:class="{ 'align-right': alignRight }"
				v-show="menuVisible"
			>
				<slot name="menu"></slot>
			</ul>
		</Transition>
	</div>
</template>

<style lang="scss">
.drop-down {
	position: relative;

	.dd-switch {
		@include field;

		&.active {
			background-color: $fuji-blue;

			span {
				color: white;
			}

			.tool-icon-wrapper {
				.tool-icon {
					color: white;
				}
			}
		}
	}

	.dd-menu {
		@include window();

		flex-direction: column;
		align-items: center;

		min-width: 202px;
		width: fit-content;
		max-height: 350px;
		margin: 0;

		position: absolute;
		z-index: 1;
		overflow-y: auto;

		white-space: nowrap;

		gap: 16px;

		list-style: none;
		padding: 24px;

		transition: opacity 0.5s;

		&.align-right {
			right: 0;
		}

		li {
			display: flex;
			flex-direction: row;

			width: 100%;

			p {
				margin: 0;
			}

			gap: 16px;

			.checkbox {
				@include checkbox;

				&.disabled.checked {
					background-color: $disabled-bg-color;
				}
			}
		}
	}
}
</style>
