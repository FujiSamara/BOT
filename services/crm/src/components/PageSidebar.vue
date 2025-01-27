<script setup lang="ts">
import FujiHeader from "@/components/FujiHeader.vue";
import { LinkData } from "@/types";

const props = defineProps({
	links: {
		type: Array<LinkData>,
		required: true,
	},
});

const sidebarFolded = defineModel({
	type: Boolean,
	required: true,
});

const emits = defineEmits<{
	(e: "change", link: LinkData): void;
}>();

const onClick = async (link: LinkData) => {
	emits("change", link);
};
</script>

<template>
	<div class="table-sidebar">
		<FujiHeader class="header" :short="sidebarFolded"></FujiHeader>
		<ul class="sb-list">
			<li
				class="sb-row"
				:class="{ active: link.active }"
				v-for="link in props.links"
				@click="() => onClick(link)"
			>
				<div class="sb-icon-wrapper">
					<div
						class="sb-icon"
						:style="`mask: url(${link.iconURL}) no-repeat`"
					></div>
				</div>
				<Transition name="fade">
					<span class="sb-link" v-if="!sidebarFolded">{{ link.label }}</span>
				</Transition>
			</li>
		</ul>
		<div class="sb-hide-wrapper">
			<div class="sb-hide" @click="sidebarFolded = !sidebarFolded">
				<div class="sb-arrow"></div>
			</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.table-sidebar {
	display: flex;
	flex-direction: column;
	justify-content: space-between;

	padding: 46px 32px 64px 32px;

	background-color: $main-white;

	.sb-list {
		display: flex;
		flex-direction: column;
		flex-grow: 1;
		gap: 26px;

		margin-top: 64px;
		margin-bottom: 0;
		padding-left: 0;

		list-style: none;

		.sb-row {
			display: flex;
			flex-direction: row;
			align-items: center;
			gap: 10px;

			position: relative;
			left: -9px;

			width: 100%;
			height: 34px;

			padding: 0 9px;

			border-left: 2px solid transparent;
			color: $main-dark-gray;
			cursor: pointer;

			transition:
				border-left-color 0.25s,
				color 0.25s;

			.sb-link {
				padding: 0;
				width: fit-content;

				font-family: Wix Madefor Display;
				font-weight: 500;
				font-size: 16px;
				line-height: 20.16px;
			}

			.sb-icon-wrapper {
				display: flex;
				justify-content: center;
				align-items: center;

				width: 24px;
				height: 24px;

				padding: 0;

				.sb-icon {
					background-color: currentColor;
					width: 15.77px;
					height: 16px;
					fill: currentColor;
					opacity: 50%;

					transition: opacity 0.25s;
				}
			}

			&:hover,
			&.active {
				.sb-icon-wrapper {
					.sb-icon {
						opacity: 100%;
					}
				}
				background-color: $bg-light-blue;
				border-left-color: $main-accent-blue;
				color: $main-accent-blue;
			}
		}
	}

	.sb-hide-wrapper {
		display: flex;
		flex-direction: row;
		justify-content: flex-end;

		width: 100%;

		padding-right: 16px;

		.sb-hide {
			display: flex;
			justify-content: center;
			align-items: center;

			width: 48px;
			height: 48px;

			transform: rotate(90deg);

			border-radius: 8px;
			background-color: $bg-accent-blue-3;
			cursor: pointer;

			transition: transform 0.25s;

			.sb-arrow {
				background-color: currentColor;
				color: $main-accent-blue;
				width: 24px;
				height: 16px;
				fill: currentColor;

				mask-size: contain;
				mask-image: url("@/assets/icons/arrow.svg");
				mask-repeat: no-repeat;
			}
		}
	}

	&.folded {
		padding: 46px 20.72px 64px 20.72px;
		.sb-hide-wrapper {
			padding: 0;

			.sb-hide {
				transform: rotate(-90deg);
			}
		}
	}
}
</style>
