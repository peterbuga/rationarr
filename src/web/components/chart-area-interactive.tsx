"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, Line, LineChart, XAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"
import useSWR from 'swr';

export const description = "An interactive area chart"

const chartConfig = {
  ratio: {
    label: "Ratio",
    color: "var(--primary)",
  },
  seed: {
    label: "Seed",
    color: "green",
  },
  leech: {
    label: "Leech",
    color: "orange",
  },
  hnr: {
    label: "HNR",
    color: "red",
  },
  points: {
    label: "Points",
    color: "yellow",
  },
  download: {
    label: "Download",
    color: "#770023",
  },
  upload: {
    label: "Upload",
    color: "#01731F",
  },
} satisfies ChartConfig

const fetcher = async (url: string) => {
  const res = await fetch(url);
  return res.json();
};

export function ChartLineMultiple(props: any) {
  const { data, isLoading, error } = useSWR(`/api/scraper/${props.indexer.id}`, fetcher, {
    refreshWhenOffline: false,
    revalidateOnFocus: false,
  });

  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("90d")
  const [filteredData, setFilteredData] = React.useState<object[]>([]);

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }

    if (!isLoading) {
      let chartData: any[] = [];

      for (const [key, entries] of Object.entries(data as Record<string, unknown>)) {
        for (const [dt, value] of Object.entries(entries as Record<string, unknown>)) {
          const foundDate = chartData.find((item: any) => item.date === dt);

          // convert bytes to megabytes
          let valueNew;
          if (['download', 'upload', 'buffer'].includes(key)) {
            valueNew = ((value as number) / 1024 / 1024).toFixed(2)
          } else {
            valueNew = value
          }

          if (!foundDate) {
            chartData.push({
              "date": dt, 
              [key+"Orig"]: valueNew, 
              [key]: valueNew as number ? Math.log10(valueNew as number) : 0
            })
          } else {
            chartData = chartData.map(item =>
              item.date === dt ? {
                ...item, 
                [key+"Orig"]: valueNew, 
                [key]: valueNew as number ? Math.log10(valueNew as number) : 0
              } : item
            );
          }
        }
      }

      const filteredData = chartData.filter((item) => {
        const date = new Date(item.date)
        const referenceDate = new Date()
        let daysToSubtract = 90
        if (timeRange === "30d") {
          daysToSubtract = 30
        } else if (timeRange === "7d") {
          daysToSubtract = 7
        }
        const startDate = new Date(referenceDate)
        startDate.setDate(startDate.getDate() - daysToSubtract)
        return date >= startDate
      })

      setFilteredData(filteredData);
    }
  }, [isMobile, data, isLoading, timeRange])

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle><span className="font-bold">{props.indexer.name}</span> stats</CardTitle>
        {/* <CardDescription>January - June 2024</CardDescription> */}
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">Last 3 months</ToggleGroupItem>
            <ToggleGroupItem value="30d">Last 30 days</ToggleGroupItem>
            <ToggleGroupItem value="7d">Last 7 days</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              size="sm"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent>
        <ChartContainer className="w-full h-[400px] max-h-[400px] overflow-hidden" config={chartConfig}>
          <LineChart
            accessibilityLayer
            data={filteredData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={true}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric"
                })
              }}
            />
            <ChartTooltip 
              cursor={true} 
              content={
                <ChartTooltipContent 
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="line"
                  formatter={(value, name, props, item, index) => {
                    // console.log(value, name, props, chartConfig[name])
                    return [chartConfig[name as keyof typeof chartConfig].label,' => ', props.payload[name+"Orig"]]
                  }} 
                />
              }
            />
            {Object.entries(chartConfig).map(([attr, value]) => {
              if (Object.keys(value).length) {
                return <Line
                  key={attr}
                  dataKey={attr}
                  type="monotone"
                  stroke={`var(--color-${attr})`}
                  strokeWidth={2}
                  dot={false}
                />
              }
            })}
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

export function ChartAreaInteractive(props: any) {
  const { data, isLoading, error } = useSWR(`/api/scraper/${props.indexer.id}`, fetcher, {
    refreshWhenOffline: false,
    revalidateOnFocus: false,
  });

  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("90d")
  const [filteredData, setFilteredData] = React.useState<object[]>([]);
  
  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }

    if (!isLoading) {
      let chartData: any[] = [];

      for (const [key, entries] of Object.entries(data as Record<string, unknown>)) {
        for (const [dt, value] of Object.entries(entries as Record<string, unknown>)) {
          const foundDate = chartData.find((item: any) => item.date === dt);
          if (!foundDate) {
            chartData.push({"date": dt, [key]: value})
          } else {
            chartData = chartData.map(item =>
              item.date === dt ? { ...item, [key]: value } : item
            );
          }
        }
      }

      const filteredData = chartData.filter((item) => {
        const date = new Date(item.date)
        const referenceDate = new Date()
        let daysToSubtract = 90
        if (timeRange === "30d") {
          daysToSubtract = 30
        } else if (timeRange === "7d") {
          daysToSubtract = 7
        }
        const startDate = new Date(referenceDate)
        startDate.setDate(startDate.getDate() - daysToSubtract)
        return date >= startDate
      })

      setFilteredData(filteredData);
    }
  }, [isMobile, data, isLoading, timeRange])

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle><span className="font-bold">{props.indexer.name}</span> stats</CardTitle>
        {/* <CardDescription>
          <span className="hidden @[540px]/card:block">
            Total for the last 3 months
          </span>
          <span className="@[540px]/card:hidden">Last 3 months</span>
        </CardDescription> */}
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">Last 3 months</ToggleGroupItem>
            <ToggleGroupItem value="30d">Last 30 days</ToggleGroupItem>
            <ToggleGroupItem value="7d">Last 7 days</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              size="sm"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillRatio" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-ratio)"
                  stopOpacity={1.0}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-ratio)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillLeech" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-leech)"
                  stopOpacity={1.0}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-leech)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillSeed" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-seed)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-seed)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillHnr" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-hnr)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-hnr)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillPoints" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-points)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-points)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={true} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={16}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric"
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="dot"
                  formatter={(value, name, props) => {
                    // console.log(value, name, props)
                    // `Profit: ${props.payload.actualProfit}`,
                    // 'Revenue'
                    return [value, name]
                  }}
                />
              }
            />
            <Area
              dataKey="ratio"
              type="natural"
              fill="url(#fillRatio)"
              stroke="var(--color-ratio)"
              stackId="a"
            />

            <Area
              dataKey="leech"
              type="natural"
              fill="url(#fillLeech)"
              stroke="var(--color-leech)"
              stackId="a"
            />
            <Area
              dataKey="seed"
              type="natural"
              fill="url(#fillSeed)"
              stroke="var(--color-seed)"
              stackId="a"
            />
            <Area
              dataKey="hnr"
              type="natural"
              fill="url(#fillHnr)"
              stroke="var(--color-hnr)"
              stackId="a"
            />
            <Area
              dataKey="points"
              type="natural"
              fill="url(#fillPoints)"
              stroke="var(--color-points)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
