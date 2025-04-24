<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { pathToRouter } from "@/components/knowledge";

const props = defineProps({
	path: {
		type: String,
		required: true,
	},
});

const router = useRouter();
const route = useRoute();

const sections = computed(() =>
	props.path.split("/").filter((val) => val.length),
);

const onClick = async (index: number) => {
	const path =
		"/" + sections.value.slice(0, index + 1).reduce((f, s) => f + "/" + s);

	const fullPath = route.path.split("knowledge")[0] + "knowledge" + path;
	await router.push({ path: pathToRouter(fullPath) });
};
</script>
<template>
	<div class="division-path">
		<span @click="onClick(i)" class="path" v-for="(section, i) in sections"
			>/{{ section }}</span
		>
	</div>
</template>
<style scoped lang="scss">
.division-path {
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;

	.path {
		position: relative;
		font-family: Wix Madefor Display;
		font-weight: 400;
		font-size: 16px;
		cursor: pointer;

		&::after {
			content: "";
			position: absolute;
			left: 0;
			bottom: 0;
			opacity: 0;
			height: 1px;
			width: 100%;
			background-color: currentColor;
			transition: opacity 0.25s;
		}

		&:hover::after {
			opacity: 1;
		}
	}
}
</style>
