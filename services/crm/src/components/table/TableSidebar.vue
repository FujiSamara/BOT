<script setup lang="ts">
import FujiHeader from "@/components/FujiHeader.vue";
</script>

<template>
	<div class="table-sidebar">
		<FujiHeader class="header"></FujiHeader>
		<ul class="list">
			<li class="sb-row">
				<div class="sb-link">Статьи</div>
			</li>
			<li class="sb-row">
				<div class="sb-icon-wrapper">
					<div class="sb-icon"></div>
				</div>
				<span class="sb-link">Выход</span>
			</li>
		</ul>
	</div>
</template>

<style scoped lang="scss">
.table-sidebar {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;

	padding: 46px 32px 64px 32px;

	background-color: $sidebar-background-color;

	.list {
		display: flex;
		flex-direction: column;
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

			padding-left: 9px;

			border-left: 2px solid transparent;
			color: $text-color;

			transition:
				border-left-color 0.3s,
				color 0.3s;

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

					mask: url("@/assets/icons/exit.svg") no-repeat;
					mask-size: cover;

					transition: opacity 0.3s;
				}
			}

			&:hover {
				.sb-icon-wrapper {
					.sb-icon {
						opacity: 100%;
					}
				}
				background-color: $body-background-color;
				border-left-color: $sidebar-link-border-color;
				color: $fuji-blue;
			}
		}
	}
}
</style>
