<script setup lang="ts">
import DropDownMenu from "@/components/DropDownMenu.vue";

import { onMounted, PropType, Ref, ref, watch } from "vue";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import { useRoute, useRouter } from "vue-router";
import { base64UrlDecode, base64UrlEncode } from "@/parser";

const props = defineProps({
	table: {
		type: Object as PropType<Table<BaseSchema>>,
		required: true,
	},
	style: {
		type: String,
	},
	alignRight: {
		type: Boolean,
	},
});

const headersHidden: Ref<Array<boolean>> = ref([]);
const oneColumnVisible = ref(false);

const route = useRoute();
const router = useRouter();

const loadFromQuery = () => {
	const query = { ...route.query };

	if ("hiddenHeaders" in query) {
		const payload = query["hiddenHeaders"] as string;
		let indices = [];
		let length = -1;
		try {
			indices = base64UrlDecode(payload)
				.split(";")
				.filter((val) => val)
				.map((val) => parseInt(val));
		} catch (e) {
			console.log(e);
			delete query["hiddenHeaders"];
			return;
		}
		length = indices[0];
		indices.splice(0, 1);

		const res = new Array(length).fill(false);

		indices.forEach((val) => (res[val] = true));
		headersHidden.value = res;
	}
};
const saveToQuery = async () => {
	const length = props.table.orderedHeaders.value.length;

	let payload = `${length};`;
	headersHidden.value.forEach((val, i) => {
		if (val) payload += `${i};`;
	});

	const query = { ...route.query };

	if (payload.split(";").length === 2 && "hiddenHeaders" in query) {
		delete query["hiddenHeaders"];
	} else {
		const encoded = base64UrlEncode(payload);
		query["hiddenHeaders"] = encoded;
	}
	await router.replace({ query: query });
};

const checkboxClicked = async (index: number) => {
	if (oneColumnVisible.value && !headersHidden.value[index]) {
		return;
	}

	const result = [...headersHidden.value];

	result[index] = !result[index];

	headersHidden.value = result;

	await saveToQuery();
};

watch(props.table.orderedHeaders, () => {
	if (headersHidden.value.length === 0) {
		headersHidden.value = props.table.orderedHeaders.value.map(() => false);
	} else {
		headersHidden.value = [...headersHidden.value];
	}
});

watch(headersHidden, () => {
	const hiddenHeaders = props.table.orderedHeaders.value.filter(
		(_, index) => headersHidden.value[index],
	);

	props.table.columnHidden.value = hiddenHeaders;

	oneColumnVisible.value =
		props.table.columnHidden.value.length ===
		props.table.orderedHeaders.value.length - 1;
});

onMounted(() => {
	loadFromQuery();
});
</script>

<template>
	<DropDownMenu :style="props.style" :align-right="props.alignRight">
		<template #title>
			<div class="tool-icon-wrapper"><div class="tool-icon filter"></div></div>
			<span>Настройка столбцов</span>
		</template>
		<template #menu>
			<li
				class="menu-list"
				v-for="(header, index) in props.table.orderedHeaders.value"
				:key="header"
			>
				<div
					class="checkbox"
					:class="{
						checked: !headersHidden[index],
						disabled: oneColumnVisible,
					}"
					@click="() => checkboxClicked(index)"
				>
					<div class="icon"></div>
				</div>
				<p>{{ header }}</p>
			</li>
		</template>
	</DropDownMenu>
</template>

<style scoped lang="scss">
.tool-icon-wrapper {
	.tool-icon {
		width: 15px;
		height: 10px;

		&.filter {
			mask-image: url("@/assets/icons/sort.svg");
		}
	}
}

.menu-list {
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
			background-color: $stroke-gray;
		}
	}
}
</style>
